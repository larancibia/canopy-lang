"""
Unit tests for portfolio backtest application service.

Tests for run_portfolio_backtest application function.
"""

import pytest
import pandas as pd
import numpy as np
from canopy.application.run_portfolio_backtest import run_portfolio_backtest
from canopy.domain.portfolio_strategy import StaticAllocationStrategy
from canopy.domain.timeseries import TimeSeries
from canopy.domain.backtest import Backtest
from canopy.adapters.engines.portfolio_engine import PortfolioBacktestEngine


class TestRunPortfolioBacktest:
    """Test portfolio backtest application service."""

    def test_run_portfolio_backtest_basic(self):
        """Test running a basic portfolio backtest."""
        # Create simple time series data
        dates = pd.date_range("2024-01-01", periods=20, freq="D")

        timeseries_data = {
            "AAPL": TimeSeries(
                symbol="AAPL",
                open=pd.Series([150.0] * 20, index=dates),
                high=pd.Series([152.0] * 20, index=dates),
                low=pd.Series([148.0] * 20, index=dates),
                close=pd.Series(np.linspace(150, 160, 20), index=dates),
                volume=pd.Series([1000000] * 20, index=dates),
            ),
            "GOOGL": TimeSeries(
                symbol="GOOGL",
                open=pd.Series([200.0] * 20, index=dates),
                high=pd.Series([202.0] * 20, index=dates),
                low=pd.Series([198.0] * 20, index=dates),
                close=pd.Series(np.linspace(200, 205, 20), index=dates),
                volume=pd.Series([1000000] * 20, index=dates),
            ),
        }

        strategy = StaticAllocationStrategy(
            name="Balanced Portfolio",
            target_weights={"AAPL": 0.5, "GOOGL": 0.5},
            rebalance_frequency=10,
        )

        engine = PortfolioBacktestEngine()

        backtest = run_portfolio_backtest(
            strategy=strategy,
            timeseries_data=timeseries_data,
            engine=engine,
            initial_capital=50000.0,
            commission=0.001,
            slippage=0.001,
        )

        # Verify results
        assert isinstance(backtest, Backtest)
        assert backtest.strategy_name == "Balanced Portfolio"
        assert backtest.initial_capital == 50000.0
        assert len(backtest.equity_curve) > 0

    def test_run_portfolio_backtest_with_default_engine(self):
        """Test running backtest with default engine."""
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
            name="100% AAPL",
            target_weights={"AAPL": 1.0},
            rebalance_frequency=5,
        )

        # Should use default engine if none provided
        backtest = run_portfolio_backtest(
            strategy=strategy,
            timeseries_data=timeseries_data,
        )

        assert isinstance(backtest, Backtest)
