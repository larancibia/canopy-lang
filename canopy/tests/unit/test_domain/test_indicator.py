"""Tests for Indicator domain entities"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from canopy.domain.timeseries import TimeSeries
from canopy.domain.indicator import Indicator, SMA, EMA, RSI


class TestSMA:
    """Test suite for Simple Moving Average"""

    @pytest.fixture
    def sample_timeseries(self) -> TimeSeries:
        """Create sample timeseries data"""
        dates = pd.date_range(start="2024-01-01", periods=20, freq="D")
        # Create a simple uptrend
        close_prices = [100.0 + i * 2 for i in range(20)]
        return TimeSeries(
            open=pd.Series(close_prices, index=dates),
            high=pd.Series([p + 5 for p in close_prices], index=dates),
            low=pd.Series([p - 5 for p in close_prices], index=dates),
            close=pd.Series(close_prices, index=dates),
            volume=pd.Series([1000.0] * 20, index=dates),
        )

    def test_sma_calculates_correct_values(self, sample_timeseries: TimeSeries) -> None:
        """Test that SMA calculates correct values"""
        sma = SMA(period=5)
        result = sma.calculate(sample_timeseries)

        assert isinstance(result, pd.Series)
        assert len(result) == len(sample_timeseries)

        # First 4 values should be NaN (not enough data for 5-period SMA)
        assert result.iloc[:4].isna().all()

        # 5th value should be average of first 5 closes
        expected_5th = (100.0 + 102.0 + 104.0 + 106.0 + 108.0) / 5
        assert pytest.approx(result.iloc[4], rel=1e-9) == expected_5th

        # Check another value (indices 5-9: values 110, 112, 114, 116, 118)
        expected_10th = (110.0 + 112.0 + 114.0 + 116.0 + 118.0) / 5
        assert pytest.approx(result.iloc[9], rel=1e-9) == expected_10th

    def test_sma_validates_period(self) -> None:
        """Test that SMA validates period parameter"""
        # Period must be positive
        with pytest.raises(ValueError):
            SMA(period=0)

        with pytest.raises(ValueError):
            SMA(period=-5)

    def test_sma_handles_insufficient_data(self) -> None:
        """Test that SMA handles insufficient data gracefully"""
        dates = pd.date_range(start="2024-01-01", periods=3, freq="D")
        ts = TimeSeries(
            open=pd.Series([100.0, 101.0, 102.0], index=dates),
            high=pd.Series([105.0, 106.0, 107.0], index=dates),
            low=pd.Series([95.0, 96.0, 97.0], index=dates),
            close=pd.Series([100.0, 101.0, 102.0], index=dates),
            volume=pd.Series([1000.0, 1100.0, 1200.0], index=dates),
        )

        sma = SMA(period=10)
        result = sma.calculate(ts)

        # All values should be NaN (not enough data)
        assert result.isna().all()

    def test_sma_period_one(self, sample_timeseries: TimeSeries) -> None:
        """Test SMA with period=1 (should equal close prices)"""
        sma = SMA(period=1)
        result = sma.calculate(sample_timeseries)

        # SMA with period 1 should equal close prices
        pd.testing.assert_series_equal(result, sample_timeseries.close, check_names=False)


class TestEMA:
    """Test suite for Exponential Moving Average"""

    @pytest.fixture
    def sample_timeseries(self) -> TimeSeries:
        """Create sample timeseries data"""
        dates = pd.date_range(start="2024-01-01", periods=20, freq="D")
        close_prices = [100.0 + i * 2 for i in range(20)]
        return TimeSeries(
            open=pd.Series(close_prices, index=dates),
            high=pd.Series([p + 5 for p in close_prices], index=dates),
            low=pd.Series([p - 5 for p in close_prices], index=dates),
            close=pd.Series(close_prices, index=dates),
            volume=pd.Series([1000.0] * 20, index=dates),
        )

    def test_ema_calculates_correct_values(self, sample_timeseries: TimeSeries) -> None:
        """Test that EMA calculates correct values"""
        ema = EMA(period=5)
        result = ema.calculate(sample_timeseries)

        assert isinstance(result, pd.Series)
        assert len(result) == len(sample_timeseries)

        # EMA should not have NaN after first value (with adjust=False)
        assert not result.iloc[1:].isna().any()

        # EMA should respond more to recent prices than SMA
        # Verify it's not equal to SMA
        sma = SMA(period=5)
        sma_result = sma.calculate(sample_timeseries)
        assert not result.iloc[-1] == sma_result.iloc[-1]

    def test_ema_validates_period(self) -> None:
        """Test that EMA validates period parameter"""
        with pytest.raises(ValueError):
            EMA(period=0)

        with pytest.raises(ValueError):
            EMA(period=-10)

    def test_ema_responds_to_recent_changes(self) -> None:
        """Test that EMA is more responsive to recent price changes"""
        dates = pd.date_range(start="2024-01-01", periods=10, freq="D")
        # Stable prices then a spike
        close_prices = [100.0] * 8 + [120.0, 130.0]

        ts = TimeSeries(
            open=pd.Series(close_prices, index=dates),
            high=pd.Series([p + 5 for p in close_prices], index=dates),
            low=pd.Series([p - 5 for p in close_prices], index=dates),
            close=pd.Series(close_prices, index=dates),
            volume=pd.Series([1000.0] * 10, index=dates),
        )

        ema = EMA(period=5)
        sma = SMA(period=5)

        ema_result = ema.calculate(ts)
        sma_result = sma.calculate(ts)

        # EMA should be higher than SMA at the end due to recent spike
        assert ema_result.iloc[-1] > sma_result.iloc[-1]


class TestRSI:
    """Test suite for Relative Strength Index"""

    @pytest.fixture
    def sample_timeseries(self) -> TimeSeries:
        """Create sample timeseries data"""
        dates = pd.date_range(start="2024-01-01", periods=30, freq="D")
        # Create data with clear trends
        close_prices = [100.0 + i for i in range(30)]
        return TimeSeries(
            open=pd.Series(close_prices, index=dates),
            high=pd.Series([p + 5 for p in close_prices], index=dates),
            low=pd.Series([p - 5 for p in close_prices], index=dates),
            close=pd.Series(close_prices, index=dates),
            volume=pd.Series([1000.0] * 30, index=dates),
        )

    def test_rsi_calculates_correct_values(self, sample_timeseries: TimeSeries) -> None:
        """Test that RSI calculates correct values"""
        rsi = RSI(period=14)
        result = rsi.calculate(sample_timeseries)

        assert isinstance(result, pd.Series)
        assert len(result) == len(sample_timeseries)

        # First few values will be NaN due to diff() and rolling
        assert result.iloc[:14].isna().any()

        # RSI should have valid values after warmup period
        assert not result.iloc[15:].isna().any()

    def test_rsi_range_0_to_100(self) -> None:
        """Test that RSI values are between 0 and 100"""
        dates = pd.date_range(start="2024-01-01", periods=30, freq="D")

        # Create highly volatile data
        np.random.seed(42)
        base_price = 100.0
        close_prices = [base_price + np.random.randn() * 10 for _ in range(30)]

        ts = TimeSeries(
            open=pd.Series(close_prices, index=dates),
            high=pd.Series([p + 5 for p in close_prices], index=dates),
            low=pd.Series([p - 5 for p in close_prices], index=dates),
            close=pd.Series(close_prices, index=dates),
            volume=pd.Series([1000.0] * 30, index=dates),
        )

        rsi = RSI(period=14)
        result = rsi.calculate(ts)

        # All non-NaN values should be between 0 and 100
        valid_values = result.dropna()
        assert (valid_values >= 0).all()
        assert (valid_values <= 100).all()

    def test_rsi_default_period(self) -> None:
        """Test that RSI has default period of 14"""
        rsi = RSI()
        assert rsi.period == 14

    def test_rsi_validates_period(self) -> None:
        """Test that RSI validates period parameter"""
        with pytest.raises(ValueError):
            RSI(period=0)

        with pytest.raises(ValueError):
            RSI(period=-7)

    def test_rsi_uptrend_high_values(self) -> None:
        """Test that RSI shows high values during strong uptrends"""
        dates = pd.date_range(start="2024-01-01", periods=30, freq="D")
        # Strong uptrend
        close_prices = [100.0 + i * 3 for i in range(30)]

        ts = TimeSeries(
            open=pd.Series(close_prices, index=dates),
            high=pd.Series([p + 5 for p in close_prices], index=dates),
            low=pd.Series([p - 5 for p in close_prices], index=dates),
            close=pd.Series(close_prices, index=dates),
            volume=pd.Series([1000.0] * 30, index=dates),
        )

        rsi = RSI(period=14)
        result = rsi.calculate(ts)

        # During strong uptrend, RSI should be high (> 70 typically indicates overbought)
        assert result.iloc[-1] > 70

    def test_rsi_downtrend_low_values(self) -> None:
        """Test that RSI shows low values during strong downtrends"""
        dates = pd.date_range(start="2024-01-01", periods=30, freq="D")
        # Strong downtrend
        close_prices = [200.0 - i * 3 for i in range(30)]

        ts = TimeSeries(
            open=pd.Series(close_prices, index=dates),
            high=pd.Series([p + 5 for p in close_prices], index=dates),
            low=pd.Series([p - 5 for p in close_prices], index=dates),
            close=pd.Series(close_prices, index=dates),
            volume=pd.Series([1000.0] * 30, index=dates),
        )

        rsi = RSI(period=14)
        result = rsi.calculate(ts)

        # During strong downtrend, RSI should be low (< 30 typically indicates oversold)
        assert result.iloc[-1] < 30


class TestIndicatorAbstract:
    """Test the abstract Indicator base class"""

    def test_indicator_is_abstract(self) -> None:
        """Test that Indicator cannot be instantiated directly"""
        with pytest.raises(TypeError):
            # Should fail because calculate() is abstract
            Indicator()  # type: ignore
