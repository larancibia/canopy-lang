"""
Unit tests for RunBacktestUseCase.

Tests the application use case layer with mocked dependencies.
"""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, MagicMock
from canopy.application.run_backtest import RunBacktestUseCase
from canopy.domain.strategy import Strategy
from canopy.domain.timeseries import TimeSeries
from canopy.domain.backtest import Backtest, Trade
from canopy.domain.metrics import PerformanceMetrics


@pytest.fixture
def mock_engine():
    """Create a mock backtest engine"""
    engine = Mock()
    return engine


@pytest.fixture
def mock_strategy():
    """Create a mock strategy"""
    strategy = Mock(spec=Strategy)
    strategy.name = "Test Strategy"
    return strategy


@pytest.fixture
def mock_timeseries():
    """Create a mock timeseries"""
    dates = pd.date_range("2024-01-01", periods=10, freq="D")
    prices = pd.Series([100, 101, 102, 103, 104, 105, 106, 107, 108, 109], index=dates)
    return TimeSeries(
        open=prices,
        high=prices + 1,
        low=prices - 1,
        close=prices,
        volume=pd.Series([1000000] * 10, index=dates)
    )


@pytest.fixture
def sample_backtest():
    """Create a sample backtest result"""
    dates = pd.date_range("2024-01-01", periods=10, freq="D")
    equity_curve = pd.Series([10000, 10100, 10200, 10150, 10300, 10400, 10350, 10500, 10600, 10700], index=dates)
    trades = [
        Trade(
            entry_time=pd.Timestamp("2024-01-01"),
            exit_time=pd.Timestamp("2024-01-05"),
            entry_price=100.0,
            exit_price=105.0,
            quantity=100.0,
            side="long",
            pnl=500.0,
            return_pct=5.0
        )
    ]
    return Backtest(
        strategy_name="Test Strategy",
        initial_capital=10000.0,
        equity_curve=equity_curve,
        trades=trades
    )


class TestRunBacktestUseCase:
    """Test RunBacktestUseCase application layer"""

    def test_run_backtest_use_case(self, mock_engine, mock_strategy, mock_timeseries, sample_backtest):
        """Use case should run backtest and calculate metrics"""
        # Arrange
        mock_engine.run.return_value = sample_backtest
        use_case = RunBacktestUseCase(mock_engine)

        # Act
        backtest, metrics = use_case.execute(
            strategy=mock_strategy,
            timeseries=mock_timeseries,
            initial_capital=10000.0
        )

        # Assert
        # Engine was called with correct parameters
        mock_engine.run.assert_called_once()
        call_args = mock_engine.run.call_args
        assert call_args[1]['strategy'] == mock_strategy
        assert call_args[1]['timeseries'] == mock_timeseries
        assert call_args[1]['initial_capital'] == 10000.0

        # Backtest result is returned
        assert backtest == sample_backtest

        # Metrics are calculated
        assert isinstance(metrics, PerformanceMetrics)
        assert metrics.total_return > 0
        assert metrics.total_trades >= 0

    def test_run_backtest_with_custom_parameters(self, mock_engine, mock_strategy, mock_timeseries, sample_backtest):
        """Use case should pass custom parameters to engine"""
        # Arrange
        mock_engine.run.return_value = sample_backtest
        use_case = RunBacktestUseCase(mock_engine)

        # Act
        backtest, metrics = use_case.execute(
            strategy=mock_strategy,
            timeseries=mock_timeseries,
            initial_capital=50000.0,
            commission=0.001,
            slippage=0.0005
        )

        # Assert
        call_args = mock_engine.run.call_args
        assert call_args[1]['initial_capital'] == 50000.0
        assert call_args[1]['commission'] == 0.001
        assert call_args[1]['slippage'] == 0.0005

    def test_run_backtest_metrics_calculation(self, mock_engine, mock_strategy, mock_timeseries, sample_backtest):
        """Use case should correctly calculate all metrics"""
        # Arrange
        mock_engine.run.return_value = sample_backtest
        use_case = RunBacktestUseCase(mock_engine)

        # Act
        backtest, metrics = use_case.execute(
            strategy=mock_strategy,
            timeseries=mock_timeseries
        )

        # Assert - all metrics should be present
        assert hasattr(metrics, 'total_return')
        assert hasattr(metrics, 'sharpe_ratio')
        assert hasattr(metrics, 'sortino_ratio')
        assert hasattr(metrics, 'max_drawdown')
        assert hasattr(metrics, 'win_rate')
        assert hasattr(metrics, 'profit_factor')
        assert hasattr(metrics, 'calmar_ratio')
        assert hasattr(metrics, 'total_trades')
        assert hasattr(metrics, 'winning_trades')
        assert hasattr(metrics, 'losing_trades')

    def test_run_backtest_with_no_trades(self, mock_engine, mock_strategy, mock_timeseries):
        """Use case should handle backtests with no trades"""
        # Arrange
        dates = pd.date_range("2024-01-01", periods=10, freq="D")
        equity_curve = pd.Series([10000] * 10, index=dates)
        backtest_no_trades = Backtest(
            strategy_name="Test Strategy",
            initial_capital=10000.0,
            equity_curve=equity_curve,
            trades=[]
        )
        mock_engine.run.return_value = backtest_no_trades
        use_case = RunBacktestUseCase(mock_engine)

        # Act
        backtest, metrics = use_case.execute(
            strategy=mock_strategy,
            timeseries=mock_timeseries
        )

        # Assert
        assert backtest.trades == []
        assert metrics.total_trades == 0
        assert metrics.win_rate == 0.0
