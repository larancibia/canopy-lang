"""
Run Backtest Use Case - Application layer for backtest execution.

This module implements the application use case for running backtests,
orchestrating the backtest engine and metrics calculation.
"""

from typing import Tuple
from canopy.ports.backtest_engine import IBacktestEngine
from canopy.domain.strategy import Strategy
from canopy.domain.timeseries import TimeSeries
from canopy.domain.backtest import Backtest
from canopy.domain.metrics import (
    PerformanceMetrics,
    sharpe_ratio,
    sortino_ratio,
    max_drawdown,
    max_drawdown_duration,
    win_rate,
    profit_factor,
    calmar_ratio,
)
import pandas as pd


def calculate_metrics(backtest: Backtest) -> PerformanceMetrics:
    """
    Calculate all performance metrics from a backtest result.

    Args:
        backtest: Backtest result object

    Returns:
        PerformanceMetrics object with all calculated metrics
    """
    # Calculate returns from equity curve
    returns = backtest.equity_curve.pct_change().dropna()

    # Calculate all metrics
    total_return = backtest.total_return()
    sharpe = sharpe_ratio(returns, risk_free_rate=0.0)
    sortino = sortino_ratio(returns, risk_free_rate=0.0)
    mdd = max_drawdown(backtest.equity_curve)
    mdd_duration = max_drawdown_duration(backtest.equity_curve)
    win_r = win_rate(backtest.trades)
    pf = profit_factor(backtest.trades)
    calmar = calmar_ratio(returns)

    # Calculate trade statistics
    total_trades = len(backtest.trades)
    winning_trades = sum(1 for t in backtest.trades if t.pnl > 0)
    losing_trades = sum(1 for t in backtest.trades if t.pnl < 0)

    winning_pnls = [t.pnl for t in backtest.trades if t.pnl > 0]
    losing_pnls = [t.pnl for t in backtest.trades if t.pnl < 0]

    average_win = sum(winning_pnls) / len(winning_pnls) if winning_pnls else 0.0
    average_loss = sum(losing_pnls) / len(losing_pnls) if losing_pnls else 0.0

    return PerformanceMetrics(
        total_return=total_return,
        sharpe_ratio=sharpe,
        sortino_ratio=sortino,
        max_drawdown=mdd,
        max_drawdown_duration=mdd_duration,
        win_rate=win_r,
        profit_factor=pf,
        calmar_ratio=calmar,
        total_trades=total_trades,
        winning_trades=winning_trades,
        losing_trades=losing_trades,
        average_win=average_win,
        average_loss=average_loss,
    )


class RunBacktestUseCase:
    """
    Application use case for running backtests.

    This class orchestrates the backtest execution and metrics calculation,
    following hexagonal architecture principles by depending on the
    IBacktestEngine port rather than a concrete implementation.
    """

    def __init__(self, backtest_engine: IBacktestEngine):
        """
        Initialize the use case with a backtest engine.

        Args:
            backtest_engine: Port interface for backtest engines
        """
        self.engine = backtest_engine

    def execute(
        self,
        strategy: Strategy,
        timeseries: TimeSeries,
        initial_capital: float = 10000.0,
        commission: float = 0.0,
        slippage: float = 0.0
    ) -> Tuple[Backtest, PerformanceMetrics]:
        """
        Execute backtest and calculate metrics.

        This method coordinates the backtest execution and metrics calculation,
        providing a clean interface for the application layer.

        Args:
            strategy: Strategy to backtest
            timeseries: Historical OHLCV data
            initial_capital: Starting capital (default $10,000)
            commission: Commission per trade as percentage (default 0.0)
            slippage: Slippage per trade as percentage (default 0.0)

        Returns:
            Tuple of (Backtest results, Performance metrics)
        """
        # Run backtest
        backtest = self.engine.run(
            strategy=strategy,
            timeseries=timeseries,
            initial_capital=initial_capital,
            commission=commission,
            slippage=slippage
        )

        # Calculate metrics
        metrics = calculate_metrics(backtest)

        return backtest, metrics
