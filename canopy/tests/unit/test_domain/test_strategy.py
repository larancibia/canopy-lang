"""Tests for Strategy domain entities"""

import pytest
import pandas as pd
from datetime import datetime

from canopy.domain.timeseries import TimeSeries
from canopy.domain.strategy import Strategy, MACrossoverStrategy
from canopy.domain.signal import Signal, SignalType


class TestStrategy:
    """Test suite for abstract Strategy base class"""

    def test_strategy_is_abstract(self) -> None:
        """Test that Strategy cannot be instantiated directly"""
        with pytest.raises(TypeError):
            # Should fail because generate_signals() is abstract
            Strategy(name="Test Strategy")  # type: ignore


class TestMACrossoverStrategy:
    """Test suite for MA Crossover Strategy"""

    @pytest.fixture
    def sample_timeseries(self) -> TimeSeries:
        """Create sample timeseries data with a clear trend"""
        dates = pd.date_range(start="2024-01-01", periods=30, freq="D")

        # Create data that will produce crossovers
        # First 10 days: downtrend (fast MA below slow MA)
        # Days 10-15: uptrend starts (fast MA crosses above)
        # Days 15-25: uptrend continues
        # Days 25-30: downtrend (fast MA crosses below)
        close_prices = (
            [110 - i for i in range(10)]  # Downtrend: 110, 109, 108...
            + [101 + i * 2 for i in range(15)]  # Uptrend: 101, 103, 105...
            + [130 - i for i in range(5)]  # Downtrend: 130, 129, 128...
        )

        return TimeSeries(
            open=pd.Series(close_prices, index=dates),
            high=pd.Series([p + 2 for p in close_prices], index=dates),
            low=pd.Series([p - 2 for p in close_prices], index=dates),
            close=pd.Series(close_prices, index=dates),
            volume=pd.Series([1000.0] * 30, index=dates),
        )

    def test_strategy_initialization(self) -> None:
        """Test creating a MA Crossover strategy"""
        strategy = MACrossoverStrategy(
            name="Test MA Cross",
            fast_period=5,
            slow_period=10,
        )

        assert strategy.name == "Test MA Cross"
        assert strategy.fast_period == 5
        assert strategy.slow_period == 10

    def test_strategy_validates_periods(self) -> None:
        """Test that strategy validates period parameters"""
        # Period must be positive
        with pytest.raises(ValueError):
            MACrossoverStrategy(name="Test", fast_period=0, slow_period=10)

        with pytest.raises(ValueError):
            MACrossoverStrategy(name="Test", fast_period=5, slow_period=-10)

    def test_strategy_generate_signals_returns_list(self, sample_timeseries: TimeSeries) -> None:
        """Test that generate_signals returns a list of Signal objects"""
        strategy = MACrossoverStrategy(
            name="Test MA Cross",
            fast_period=5,
            slow_period=10,
        )

        signals = strategy.generate_signals(sample_timeseries)

        assert isinstance(signals, list)
        # Should have at least some signals
        assert len(signals) > 0
        # All elements should be Signal objects
        assert all(isinstance(s, Signal) for s in signals)

    def test_strategy_generates_buy_and_sell_signals(self, sample_timeseries: TimeSeries) -> None:
        """Test that strategy generates both buy and sell signals"""
        strategy = MACrossoverStrategy(
            name="Test MA Cross",
            fast_period=5,
            slow_period=10,
        )

        signals = strategy.generate_signals(sample_timeseries)

        buy_signals = [s for s in signals if s.type == SignalType.BUY]
        sell_signals = [s for s in signals if s.type == SignalType.SELL]

        # Should have at least one of each type
        assert len(buy_signals) > 0
        assert len(sell_signals) > 0

    def test_strategy_signal_has_reason(self, sample_timeseries: TimeSeries) -> None:
        """Test that generated signals have a reason"""
        strategy = MACrossoverStrategy(
            name="Test MA Cross",
            fast_period=5,
            slow_period=10,
        )

        signals = strategy.generate_signals(sample_timeseries)

        # All signals should have a reason
        assert all(s.reason is not None for s in signals)

        # Reasons should mention the MA periods
        for signal in signals:
            assert "5" in signal.reason  # fast_period
            assert "10" in signal.reason  # slow_period

    def test_strategy_signal_prices_match_timeseries(self, sample_timeseries: TimeSeries) -> None:
        """Test that signal prices match the timeseries close prices"""
        strategy = MACrossoverStrategy(
            name="Test MA Cross",
            fast_period=5,
            slow_period=10,
        )

        signals = strategy.generate_signals(sample_timeseries)

        # All signal prices should exist in the timeseries
        for signal in signals:
            assert signal.price in sample_timeseries.close.values

    def test_strategy_with_short_timeseries(self) -> None:
        """Test strategy with insufficient data"""
        dates = pd.date_range(start="2024-01-01", periods=5, freq="D")
        ts = TimeSeries(
            open=pd.Series([100, 101, 102, 103, 104], index=dates),
            high=pd.Series([105, 106, 107, 108, 109], index=dates),
            low=pd.Series([95, 96, 97, 98, 99], index=dates),
            close=pd.Series([100, 101, 102, 103, 104], index=dates),
            volume=pd.Series([1000, 1100, 1200, 1300, 1400], index=dates),
        )

        strategy = MACrossoverStrategy(
            name="Test MA Cross",
            fast_period=5,
            slow_period=10,
        )

        signals = strategy.generate_signals(ts)

        # With only 5 data points and a 10-period slow MA, we shouldn't get any signals
        assert len(signals) == 0

    def test_strategy_buy_when_fast_crosses_above_slow(self) -> None:
        """Test that BUY signal is generated when fast MA crosses above slow MA"""
        dates = pd.date_range(start="2024-01-01", periods=20, freq="D")

        # Create clear crossover: prices go from low to high
        close_prices = [100 - i for i in range(10)] + [91 + i * 2 for i in range(10)]

        ts = TimeSeries(
            open=pd.Series(close_prices, index=dates),
            high=pd.Series([p + 2 for p in close_prices], index=dates),
            low=pd.Series([p - 2 for p in close_prices], index=dates),
            close=pd.Series(close_prices, index=dates),
            volume=pd.Series([1000.0] * 20, index=dates),
        )

        strategy = MACrossoverStrategy(
            name="Test MA Cross",
            fast_period=3,
            slow_period=7,
        )

        signals = strategy.generate_signals(ts)
        buy_signals = [s for s in signals if s.type == SignalType.BUY]

        # Should have at least one buy signal
        assert len(buy_signals) > 0

        # Buy signals should have appropriate reason
        for signal in buy_signals:
            assert "above" in signal.reason.lower() or "crossed" in signal.reason.lower()

    def test_strategy_sell_when_fast_crosses_below_slow(self) -> None:
        """Test that SELL signal is generated when fast MA crosses below slow MA"""
        dates = pd.date_range(start="2024-01-01", periods=20, freq="D")

        # Create clear crossunder: prices go from high to low
        close_prices = [100 + i * 2 for i in range(10)] + [120 - i for i in range(10)]

        ts = TimeSeries(
            open=pd.Series(close_prices, index=dates),
            high=pd.Series([p + 2 for p in close_prices], index=dates),
            low=pd.Series([p - 2 for p in close_prices], index=dates),
            close=pd.Series(close_prices, index=dates),
            volume=pd.Series([1000.0] * 20, index=dates),
        )

        strategy = MACrossoverStrategy(
            name="Test MA Cross",
            fast_period=3,
            slow_period=7,
        )

        signals = strategy.generate_signals(ts)
        sell_signals = [s for s in signals if s.type == SignalType.SELL]

        # Should have at least one sell signal
        assert len(sell_signals) > 0

        # Sell signals should have appropriate reason
        for signal in sell_signals:
            assert "below" in signal.reason.lower() or "crossed" in signal.reason.lower()

    def test_strategy_signals_are_chronological(self, sample_timeseries: TimeSeries) -> None:
        """Test that signals are generated in chronological order"""
        strategy = MACrossoverStrategy(
            name="Test MA Cross",
            fast_period=5,
            slow_period=10,
        )

        signals = strategy.generate_signals(sample_timeseries)

        if len(signals) > 1:
            # Check that timestamps are in ascending order
            for i in range(len(signals) - 1):
                assert signals[i].timestamp <= signals[i + 1].timestamp

    def test_strategy_with_equal_periods(self) -> None:
        """Test strategy behavior when fast and slow periods are equal"""
        dates = pd.date_range(start="2024-01-01", periods=20, freq="D")
        close_prices = [100 + i for i in range(20)]

        ts = TimeSeries(
            open=pd.Series(close_prices, index=dates),
            high=pd.Series([p + 2 for p in close_prices], index=dates),
            low=pd.Series([p - 2 for p in close_prices], index=dates),
            close=pd.Series(close_prices, index=dates),
            volume=pd.Series([1000.0] * 20, index=dates),
        )

        strategy = MACrossoverStrategy(
            name="Test MA Cross",
            fast_period=5,
            slow_period=5,
        )

        signals = strategy.generate_signals(ts)

        # When periods are equal, MAs are identical, so no crossovers should occur
        assert len(signals) == 0
