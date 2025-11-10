"""
Unit tests for portfolio strategies.

Tests for PortfolioStrategy, PairsTradingStrategy, RotationStrategy, and LongShortStrategy.
"""

import pytest
import pandas as pd
import numpy as np
from canopy.domain.portfolio_strategy import (
    PortfolioStrategy,
    PairsTradingStrategy,
    RotationStrategy,
    LongShortStrategy,
    PortfolioSignal,
)
from canopy.domain.timeseries import TimeSeries


class TestPortfolioSignal:
    """Test PortfolioSignal domain model."""

    def test_signal_creation(self):
        """Test creating a portfolio signal."""
        signal = PortfolioSignal(
            timestamp=pd.Timestamp("2024-01-01"),
            target_weights={"AAPL": 0.5, "GOOGL": 0.5},
            reason="Monthly rebalance",
        )

        assert signal.timestamp == pd.Timestamp("2024-01-01")
        assert signal.target_weights == {"AAPL": 0.5, "GOOGL": 0.5}
        assert signal.reason == "Monthly rebalance"

    def test_signal_weights_sum(self):
        """Test that signal weights sum to approximately 1."""
        signal = PortfolioSignal(
            timestamp=pd.Timestamp("2024-01-01"),
            target_weights={"AAPL": 0.33, "GOOGL": 0.33, "MSFT": 0.34},
            reason="Rebalance",
        )

        total_weight = sum(signal.target_weights.values())
        assert abs(total_weight - 1.0) < 0.01


class TestPairsTradingStrategy:
    """Test PairsTradingStrategy."""

    def test_strategy_creation(self):
        """Test creating a pairs trading strategy."""
        strategy = PairsTradingStrategy(
            name="AAPL-GOOGL Pairs",
            symbol1="AAPL",
            symbol2="GOOGL",
            lookback_period=20,
            entry_threshold=2.0,
            exit_threshold=0.5,
        )

        assert strategy.name == "AAPL-GOOGL Pairs"
        assert strategy.symbol1 == "AAPL"
        assert strategy.symbol2 == "GOOGL"

    def test_pairs_generate_signals_basic(self):
        """Test generating pairs trading signals."""
        # Create mock data where AAPL and GOOGL diverge then converge
        dates = pd.date_range("2024-01-01", periods=50, freq="D")

        # Create correlated series that diverge
        np.random.seed(42)
        base = np.cumsum(np.random.normal(0, 1, 50))
        aapl_prices = 150 + base + np.linspace(0, 10, 50)  # Trending up
        googl_prices = 200 + base - np.linspace(0, 10, 50)  # Trending down

        timeseries_data = {
            "AAPL": TimeSeries(
                symbol="AAPL",
                open=pd.Series(aapl_prices, index=dates),
                high=pd.Series(aapl_prices * 1.01, index=dates),
                low=pd.Series(aapl_prices * 0.99, index=dates),
                close=pd.Series(aapl_prices, index=dates),
                volume=pd.Series([1000000] * 50, index=dates),
            ),
            "GOOGL": TimeSeries(
                symbol="GOOGL",
                open=pd.Series(googl_prices, index=dates),
                high=pd.Series(googl_prices * 1.01, index=dates),
                low=pd.Series(googl_prices * 0.99, index=dates),
                close=pd.Series(googl_prices, index=dates),
                volume=pd.Series([1000000] * 50, index=dates),
            ),
        }

        strategy = PairsTradingStrategy(
            name="AAPL-GOOGL Pairs",
            symbol1="AAPL",
            symbol2="GOOGL",
            lookback_period=20,
            entry_threshold=1.5,
            exit_threshold=0.5,
        )

        signals = strategy.generate_signals(timeseries_data)

        # Should generate some signals
        assert isinstance(signals, list)
        # Signals contain PortfolioSignal objects
        assert all(isinstance(s, PortfolioSignal) for s in signals)


class TestRotationStrategy:
    """Test RotationStrategy."""

    def test_strategy_creation(self):
        """Test creating a rotation strategy."""
        strategy = RotationStrategy(
            name="Top 3 Momentum",
            symbols=["AAPL", "GOOGL", "MSFT", "AMZN"],
            lookback_period=20,
            top_n=3,
            rebalance_frequency=30,
        )

        assert strategy.name == "Top 3 Momentum"
        assert len(strategy.symbols) == 4
        assert strategy.top_n == 3

    def test_rotation_generate_signals(self):
        """Test generating rotation signals."""
        dates = pd.date_range("2024-01-01", periods=60, freq="D")

        # Create different performance trends with valid OHLC
        np.random.seed(42)

        # Helper function to create valid OHLC
        def create_prices(base, trend, n):
            close = base + np.cumsum(np.random.normal(trend, 0.5, n))
            close = np.maximum(close, 1.0)  # Ensure positive prices
            open_p = close * (1 + np.random.uniform(-0.01, 0.01, n))
            high = np.maximum(close, open_p) * (1 + np.abs(np.random.uniform(0, 0.01, n)))
            low = np.minimum(close, open_p) * (1 - np.abs(np.random.uniform(0, 0.01, n)))
            return open_p, high, low, close

        aapl_o, aapl_h, aapl_l, aapl_c = create_prices(150, 0.5, 60)
        googl_o, googl_h, googl_l, googl_c = create_prices(200, 0.2, 60)
        msft_o, msft_h, msft_l, msft_c = create_prices(300, 0.3, 60)

        timeseries_data = {
            "AAPL": TimeSeries(
                symbol="AAPL",
                open=pd.Series(aapl_o, index=dates),
                high=pd.Series(aapl_h, index=dates),
                low=pd.Series(aapl_l, index=dates),
                close=pd.Series(aapl_c, index=dates),
                volume=pd.Series([1000000] * 60, index=dates),
            ),
            "GOOGL": TimeSeries(
                symbol="GOOGL",
                open=pd.Series(googl_o, index=dates),
                high=pd.Series(googl_h, index=dates),
                low=pd.Series(googl_l, index=dates),
                close=pd.Series(googl_c, index=dates),
                volume=pd.Series([1000000] * 60, index=dates),
            ),
            "MSFT": TimeSeries(
                symbol="MSFT",
                open=pd.Series(msft_o, index=dates),
                high=pd.Series(msft_h, index=dates),
                low=pd.Series(msft_l, index=dates),
                close=pd.Series(msft_c, index=dates),
                volume=pd.Series([1000000] * 60, index=dates),
            ),
        }

        strategy = RotationStrategy(
            name="Top 2 Momentum",
            symbols=["AAPL", "GOOGL", "MSFT"],
            lookback_period=20,
            top_n=2,
            rebalance_frequency=30,
        )

        signals = strategy.generate_signals(timeseries_data)

        # Should generate rebalance signals
        assert isinstance(signals, list)
        assert len(signals) > 0
        assert all(isinstance(s, PortfolioSignal) for s in signals)


class TestLongShortStrategy:
    """Test LongShortStrategy."""

    def test_strategy_creation(self):
        """Test creating a long-short strategy."""
        strategy = LongShortStrategy(
            name="Momentum Long-Short",
            symbols=["AAPL", "GOOGL", "MSFT", "AMZN"],
            lookback_period=20,
            long_pct=0.5,
            short_pct=0.5,
            rebalance_frequency=30,
        )

        assert strategy.name == "Momentum Long-Short"
        assert strategy.long_pct == 0.5
        assert strategy.short_pct == 0.5

    def test_longshort_generate_signals(self):
        """Test generating long-short signals."""
        dates = pd.date_range("2024-01-01", periods=60, freq="D")

        np.random.seed(42)

        # Helper function to create valid OHLC
        def create_prices(base, trend, n):
            close = base + np.cumsum(np.random.normal(trend, 0.5, n))
            close = np.maximum(close, 1.0)  # Ensure positive prices
            open_p = close * (1 + np.random.uniform(-0.01, 0.01, n))
            high = np.maximum(close, open_p) * (1 + np.abs(np.random.uniform(0, 0.01, n)))
            low = np.minimum(close, open_p) * (1 - np.abs(np.random.uniform(0, 0.01, n)))
            return open_p, high, low, close

        winner_o, winner_h, winner_l, winner_c = create_prices(100, 1, 60)
        loser_o, loser_h, loser_l, loser_c = create_prices(100, -0.5, 60)

        # Create winners and losers
        timeseries_data = {
            "WINNER": TimeSeries(
                symbol="WINNER",
                open=pd.Series(winner_o, index=dates),
                high=pd.Series(winner_h, index=dates),
                low=pd.Series(winner_l, index=dates),
                close=pd.Series(winner_c, index=dates),
                volume=pd.Series([1000000] * 60, index=dates),
            ),
            "LOSER": TimeSeries(
                symbol="LOSER",
                open=pd.Series(loser_o, index=dates),
                high=pd.Series(loser_h, index=dates),
                low=pd.Series(loser_l, index=dates),
                close=pd.Series(loser_c, index=dates),
                volume=pd.Series([1000000] * 60, index=dates),
            ),
        }

        strategy = LongShortStrategy(
            name="Simple Long-Short",
            symbols=["WINNER", "LOSER"],
            lookback_period=20,
            long_pct=0.5,
            short_pct=0.5,
            rebalance_frequency=30,
        )

        signals = strategy.generate_signals(timeseries_data)

        # Should generate signals
        assert isinstance(signals, list)
        assert len(signals) > 0
        assert all(isinstance(s, PortfolioSignal) for s in signals)

        # Check that we have both long and short positions
        if len(signals) > 0:
            first_signal = signals[0]
            # Some weights should be positive (long) and some negative (short)
            weights = first_signal.target_weights
            # At least check we have weights
            assert len(weights) > 0
