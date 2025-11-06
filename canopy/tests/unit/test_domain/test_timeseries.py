"""Tests for TimeSeries domain entity"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from canopy.domain.timeseries import TimeSeries


class TestTimeSeries:
    """Test suite for TimeSeries"""

    @pytest.fixture
    def sample_data(self) -> dict[str, pd.Series]:
        """Create sample OHLCV data"""
        dates = pd.date_range(start="2024-01-01", periods=10, freq="D")
        return {
            "open": pd.Series([100.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0, 108.0, 109.0], index=dates),
            "high": pd.Series([105.0, 106.0, 107.0, 108.0, 109.0, 110.0, 111.0, 112.0, 113.0, 114.0], index=dates),
            "low": pd.Series([95.0, 96.0, 97.0, 98.0, 99.0, 100.0, 101.0, 102.0, 103.0, 104.0], index=dates),
            "close": pd.Series([102.0, 103.0, 104.0, 105.0, 106.0, 107.0, 108.0, 109.0, 110.0, 111.0], index=dates),
            "volume": pd.Series([1000.0, 1100.0, 1200.0, 1300.0, 1400.0, 1500.0, 1600.0, 1700.0, 1800.0, 1900.0], index=dates),
        }

    def test_timeseries_stores_ohlcv_data(self, sample_data: dict[str, pd.Series]) -> None:
        """Test that TimeSeries correctly stores OHLCV data"""
        ts = TimeSeries(**sample_data)

        assert ts.open is not None
        assert ts.high is not None
        assert ts.low is not None
        assert ts.close is not None
        assert ts.volume is not None

        assert len(ts.open) == 10
        assert len(ts.high) == 10
        assert len(ts.low) == 10
        assert len(ts.close) == 10
        assert len(ts.volume) == 10

        assert ts.close.iloc[0] == 102.0
        assert ts.close.iloc[-1] == 111.0

    def test_timeseries_indexing_by_position(self, sample_data: dict[str, pd.Series]) -> None:
        """Test indexing TimeSeries by position"""
        ts = TimeSeries(**sample_data)

        # Test positive indexing
        bar = ts[0]
        assert bar["open"] == 100.0
        assert bar["high"] == 105.0
        assert bar["low"] == 95.0
        assert bar["close"] == 102.0
        assert bar["volume"] == 1000.0

        # Test negative indexing
        bar = ts[-1]
        assert bar["close"] == 111.0

        # Test middle index
        bar = ts[5]
        assert bar["close"] == 107.0

    def test_timeseries_slicing(self, sample_data: dict[str, pd.Series]) -> None:
        """Test slicing TimeSeries"""
        ts = TimeSeries(**sample_data)

        # Test slice
        sliced = ts[2:5]
        assert isinstance(sliced, TimeSeries)
        assert len(sliced) == 3
        assert sliced.close.iloc[0] == 104.0
        assert sliced.close.iloc[-1] == 106.0

        # Test slice with step
        sliced = ts[0:10:2]
        assert len(sliced) == 5
        assert sliced.close.iloc[0] == 102.0

    def test_timeseries_length(self, sample_data: dict[str, pd.Series]) -> None:
        """Test len() on TimeSeries"""
        ts = TimeSeries(**sample_data)
        assert len(ts) == 10

        sliced = ts[3:7]
        assert len(sliced) == 4

    def test_timeseries_validates_data(self) -> None:
        """Test that TimeSeries validates data consistency"""
        dates = pd.date_range(start="2024-01-01", periods=5, freq="D")

        # Test mismatched lengths
        with pytest.raises(ValueError, match="All series must have the same length"):
            TimeSeries(
                open=pd.Series([100.0, 101.0], index=dates[:2]),
                high=pd.Series([105.0, 106.0, 107.0], index=dates[:3]),
                low=pd.Series([95.0, 96.0], index=dates[:2]),
                close=pd.Series([102.0, 103.0], index=dates[:2]),
                volume=pd.Series([1000.0, 1100.0], index=dates[:2]),
            )

    def test_timeseries_validates_ohlc_relationship(self) -> None:
        """Test that TimeSeries validates OHLC relationships (high >= low, etc.)"""
        dates = pd.date_range(start="2024-01-01", periods=3, freq="D")

        # Test high < low (invalid)
        with pytest.raises(ValueError, match="High must be >= Low"):
            TimeSeries(
                open=pd.Series([100.0, 101.0, 102.0], index=dates),
                high=pd.Series([90.0, 91.0, 92.0], index=dates),  # high < low
                low=pd.Series([95.0, 96.0, 97.0], index=dates),
                close=pd.Series([102.0, 103.0, 104.0], index=dates),
                volume=pd.Series([1000.0, 1100.0, 1200.0], index=dates),
            )

    def test_timeseries_empty_data(self) -> None:
        """Test TimeSeries with empty data"""
        dates = pd.date_range(start="2024-01-01", periods=0, freq="D")
        ts = TimeSeries(
            open=pd.Series([], dtype=float, index=dates),
            high=pd.Series([], dtype=float, index=dates),
            low=pd.Series([], dtype=float, index=dates),
            close=pd.Series([], dtype=float, index=dates),
            volume=pd.Series([], dtype=float, index=dates),
        )
        assert len(ts) == 0

    def test_timeseries_to_dataframe(self, sample_data: dict[str, pd.Series]) -> None:
        """Test converting TimeSeries to DataFrame"""
        ts = TimeSeries(**sample_data)
        df = ts.to_dataframe()

        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == ["open", "high", "low", "close", "volume"]
        assert len(df) == 10
        assert df["close"].iloc[0] == 102.0

    def test_timeseries_from_dataframe(self, sample_data: dict[str, pd.Series]) -> None:
        """Test creating TimeSeries from DataFrame"""
        df = pd.DataFrame(sample_data)
        ts = TimeSeries.from_dataframe(df)

        assert isinstance(ts, TimeSeries)
        assert len(ts) == 10
        assert ts.close.iloc[0] == 102.0
