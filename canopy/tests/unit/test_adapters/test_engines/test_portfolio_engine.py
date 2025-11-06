"""
Unit tests for portfolio backtest engine.

Tests for PortfolioBacktestEngine adapter.
"""

import pytest
import pandas as pd
import numpy as np
from canopy.adapters.engines.portfolio_engine import PortfolioBacktestEngine
from canopy.domain.portfolio_strategy import StaticAllocationStrategy, RotationStrategy
from canopy.domain.timeseries import TimeSeries
from canopy.domain.backtest import Backtest


class TestPortfolioBacktestEngine:
    """Test portfolio backtest engine adapter."""

    def test_engine_creation(self):
        """Test creating a portfolio backtest engine."""
        engine = PortfolioBacktestEngine()
        assert engine is not None

    def test_static_allocation_backtest(self):
        """Test backtesting a static allocation strategy."""
        # Create simple time series data
        dates = pd.date_range("2024-01-01", periods=30, freq="D")

        timeseries_data = {
            "AAPL": TimeSeries(
                symbol="AAPL",
                open=pd.Series([150.0] * 30, index=dates),
                high=pd.Series([152.0] * 30, index=dates),
                low=pd.Series([148.0] * 30, index=dates),
                close=pd.Series(np.linspace(150, 165, 30), index=dates),
                volume=pd.Series([1000000] * 30, index=dates),
            ),
            "GOOGL": TimeSeries(
                symbol="GOOGL",
                open=pd.Series([200.0] * 30, index=dates),
                high=pd.Series([202.0] * 30, index=dates),
                low=pd.Series([198.0] * 30, index=dates),
                close=pd.Series(np.linspace(200, 210, 30), index=dates),
                volume=pd.Series([1000000] * 30, index=dates),
            ),
        }

        strategy = StaticAllocationStrategy(
            name="60/40 Portfolio",
            target_weights={"AAPL": 0.6, "GOOGL": 0.4},
            rebalance_frequency=10,
        )

        engine = PortfolioBacktestEngine()
        backtest = engine.run(
            strategy=strategy,
            timeseries_data=timeseries_data,
            initial_capital=100000.0,
            commission=0.001,
            slippage=0.001,
        )

        # Verify backtest results
        assert isinstance(backtest, Backtest)
        assert backtest.initial_capital == 100000.0
        assert len(backtest.equity_curve) > 0
        assert backtest.final_equity() > 0

    def test_rotation_strategy_backtest(self):
        """Test backtesting a rotation strategy."""
        dates = pd.date_range("2024-01-01", periods=60, freq="D")

        np.random.seed(42)

        # Helper to create valid OHLC
        def create_ts(symbol, base, trend, n, dates_idx):
            close = base + np.cumsum(np.random.normal(trend, 0.5, n))
            close = np.maximum(close, 1.0)
            open_p = close * (1 + np.random.uniform(-0.01, 0.01, n))
            high = np.maximum(close, open_p) * (1 + np.abs(np.random.uniform(0, 0.01, n)))
            low = np.minimum(close, open_p) * (1 - np.abs(np.random.uniform(0, 0.01, n)))

            return TimeSeries(
                symbol=symbol,
                open=pd.Series(open_p, index=dates_idx),
                high=pd.Series(high, index=dates_idx),
                low=pd.Series(low, index=dates_idx),
                close=pd.Series(close, index=dates_idx),
                volume=pd.Series([1000000] * n, index=dates_idx),
            )

        timeseries_data = {
            "AAPL": create_ts("AAPL", 150, 0.5, 60, dates),
            "GOOGL": create_ts("GOOGL", 200, 0.3, 60, dates),
            "MSFT": create_ts("MSFT", 300, 0.2, 60, dates),
        }

        strategy = RotationStrategy(
            name="Top 2 Momentum",
            symbols=["AAPL", "GOOGL", "MSFT"],
            lookback_period=20,
            top_n=2,
            rebalance_frequency=30,
        )

        engine = PortfolioBacktestEngine()
        backtest = engine.run(
            strategy=strategy,
            timeseries_data=timeseries_data,
            initial_capital=100000.0,
        )

        # Verify backtest results
        assert isinstance(backtest, Backtest)
        assert backtest.initial_capital == 100000.0
        assert len(backtest.equity_curve) > 0

    def test_empty_timeseries_raises_error(self):
        """Test that empty timeseries raises an error."""
        strategy = StaticAllocationStrategy(
            name="Test",
            target_weights={"AAPL": 1.0},
            rebalance_frequency=10,
        )

        engine = PortfolioBacktestEngine()

        with pytest.raises(ValueError, match="Timeseries data must not be empty"):
            engine.run(
                strategy=strategy,
                timeseries_data={},
                initial_capital=100000.0,
            )

    def test_invalid_capital_raises_error(self):
        """Test that invalid capital raises an error."""
        dates = pd.date_range("2024-01-01", periods=10, freq="D")

        timeseries_data = {
            "AAPL": TimeSeries(
                symbol="AAPL",
                open=pd.Series([150.0] * 10, index=dates),
                high=pd.Series([152.0] * 10, index=dates),
                low=pd.Series([148.0] * 10, index=dates),
                close=pd.Series([150.0] * 10, index=dates),
                volume=pd.Series([1000000] * 10, index=dates),
            ),
        }

        strategy = StaticAllocationStrategy(
            name="Test",
            target_weights={"AAPL": 1.0},
            rebalance_frequency=10,
        )

        engine = PortfolioBacktestEngine()

        with pytest.raises(ValueError, match="Initial capital must be positive"):
            engine.run(
                strategy=strategy,
                timeseries_data=timeseries_data,
                initial_capital=-1000.0,
            )
