"""
Integration tests for SimpleBacktestEngine.

Tests the complete backtest engine with real strategies and data.
"""
import pytest
import pandas as pd
import numpy as np
from canopy.adapters.engines.simple_engine import SimpleBacktestEngine
from canopy.domain.strategy import MACrossoverStrategy
from canopy.domain.timeseries import TimeSeries


@pytest.fixture
def sample_timeseries():
    """Create sample OHLCV data for testing"""
    dates = pd.date_range("2024-01-01", periods=100, freq="D")
    np.random.seed(42)

    # Generate realistic price data
    close_prices = 100 + np.cumsum(np.random.randn(100) * 2)
    high_prices = close_prices + np.abs(np.random.randn(100) * 1)
    low_prices = close_prices - np.abs(np.random.randn(100) * 1)
    open_prices = close_prices + np.random.randn(100) * 0.5
    volumes = np.random.randint(1000000, 10000000, 100)

    return TimeSeries(
        open=pd.Series(open_prices, index=dates),
        high=pd.Series(high_prices, index=dates),
        low=pd.Series(low_prices, index=dates),
        close=pd.Series(close_prices, index=dates),
        volume=pd.Series(volumes, index=dates)
    )


@pytest.fixture
def ma_crossover_strategy():
    """Create a simple MA crossover strategy"""
    return MACrossoverStrategy(
        name="MA Crossover 10/30",
        fast_period=10,
        slow_period=30
    )


class TestSimpleBacktestEngine:
    """Test SimpleBacktestEngine adapter"""

    def test_simple_engine_runs_backtest(self, sample_timeseries, ma_crossover_strategy):
        """Simple engine should run a complete backtest"""
        # Arrange
        engine = SimpleBacktestEngine()

        # Act
        backtest = engine.run(
            strategy=ma_crossover_strategy,
            timeseries=sample_timeseries,
            initial_capital=10000.0,
            commission=0.0,
            slippage=0.0
        )

        # Assert
        assert backtest is not None
        assert backtest.strategy_name == "MA Crossover 10/30"
        assert backtest.initial_capital == 10000.0
        assert len(backtest.equity_curve) > 0
        assert isinstance(backtest.trades, list)

    def test_simple_engine_handles_commissions(self, sample_timeseries, ma_crossover_strategy):
        """Simple engine should properly apply commissions"""
        # Arrange
        engine = SimpleBacktestEngine()

        # Act
        backtest_no_commission = engine.run(
            strategy=ma_crossover_strategy,
            timeseries=sample_timeseries,
            initial_capital=10000.0,
            commission=0.0,
            slippage=0.0
        )

        backtest_with_commission = engine.run(
            strategy=ma_crossover_strategy,
            timeseries=sample_timeseries,
            initial_capital=10000.0,
            commission=0.001,  # 0.1% commission
            slippage=0.0
        )

        # Assert
        # With commissions, final equity should be lower
        if len(backtest_no_commission.trades) > 0:
            assert backtest_with_commission.final_equity() <= backtest_no_commission.final_equity()

    def test_simple_engine_handles_slippage(self, sample_timeseries, ma_crossover_strategy):
        """Simple engine should properly apply slippage"""
        # Arrange
        engine = SimpleBacktestEngine()

        # Act
        backtest_no_slippage = engine.run(
            strategy=ma_crossover_strategy,
            timeseries=sample_timeseries,
            initial_capital=10000.0,
            commission=0.0,
            slippage=0.0
        )

        backtest_with_slippage = engine.run(
            strategy=ma_crossover_strategy,
            timeseries=sample_timeseries,
            initial_capital=10000.0,
            commission=0.0,
            slippage=0.001  # 0.1% slippage
        )

        # Assert
        # With slippage, final equity should be lower or equal
        if len(backtest_no_slippage.trades) > 0:
            assert backtest_with_slippage.final_equity() <= backtest_no_slippage.final_equity()

    def test_simple_engine_long_only_trades(self, sample_timeseries, ma_crossover_strategy):
        """Simple engine should generate long-only trades"""
        # Arrange
        engine = SimpleBacktestEngine()

        # Act
        backtest = engine.run(
            strategy=ma_crossover_strategy,
            timeseries=sample_timeseries,
            initial_capital=10000.0,
            commission=0.0,
            slippage=0.0
        )

        # Assert
        for trade in backtest.trades:
            assert trade.side == "long"
            assert trade.quantity > 0
            assert trade.entry_time < trade.exit_time

    def test_simple_engine_equity_curve_consistency(self, sample_timeseries, ma_crossover_strategy):
        """Equity curve should be consistent with initial and final capital"""
        # Arrange
        engine = SimpleBacktestEngine()
        initial_capital = 10000.0

        # Act
        backtest = engine.run(
            strategy=ma_crossover_strategy,
            timeseries=sample_timeseries,
            initial_capital=initial_capital,
            commission=0.0,
            slippage=0.0
        )

        # Assert
        assert backtest.equity_curve.iloc[0] == initial_capital
        assert backtest.final_equity() == backtest.equity_curve.iloc[-1]

    def test_simple_engine_trade_pnl_sum(self, sample_timeseries, ma_crossover_strategy):
        """Sum of trade PnLs should match total return"""
        # Arrange
        engine = SimpleBacktestEngine()
        initial_capital = 10000.0

        # Act
        backtest = engine.run(
            strategy=ma_crossover_strategy,
            timeseries=sample_timeseries,
            initial_capital=initial_capital,
            commission=0.0,
            slippage=0.0
        )

        # Assert
        if len(backtest.trades) > 0:
            total_pnl = sum(trade.pnl for trade in backtest.trades)
            expected_final = initial_capital + total_pnl
            # Allow for small floating point errors
            assert abs(backtest.final_equity() - expected_final) < 0.01
