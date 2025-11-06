"""
Portfolio backtest application service.

This module provides the application-level function for running portfolio backtests,
coordinating between the domain layer and infrastructure adapters.
"""

from typing import Dict, Optional
from canopy.domain.portfolio_strategy import PortfolioStrategy
from canopy.domain.timeseries import TimeSeries
from canopy.domain.backtest import Backtest
from canopy.ports.portfolio_backtest_engine import IPortfolioBacktestEngine
from canopy.adapters.engines.portfolio_engine import PortfolioBacktestEngine


def run_portfolio_backtest(
    strategy: PortfolioStrategy,
    timeseries_data: Dict[str, TimeSeries],
    engine: Optional[IPortfolioBacktestEngine] = None,
    initial_capital: float = 100000.0,
    commission: float = 0.0,
    slippage: float = 0.0,
) -> Backtest:
    """
    Run a portfolio backtest.

    This is the main application service for portfolio backtesting. It coordinates
    between the strategy (domain), time series data, and the backtest engine (adapter).

    Args:
        strategy: Portfolio strategy to backtest
        timeseries_data: Dictionary mapping symbol to TimeSeries data
        engine: Backtest engine to use (defaults to PortfolioBacktestEngine)
        initial_capital: Starting capital (default $100,000)
        commission: Commission per trade as percentage (default 0.0)
        slippage: Slippage per trade as percentage (default 0.0)

    Returns:
        Backtest object containing results

    Raises:
        ValueError: If inputs are invalid

    Example:
        >>> from canopy.domain.portfolio_strategy import StaticAllocationStrategy
        >>> from canopy.domain.timeseries import TimeSeries
        >>> import pandas as pd
        >>>
        >>> # Create strategy
        >>> strategy = StaticAllocationStrategy(
        ...     name="60/40 Portfolio",
        ...     target_weights={"AAPL": 0.6, "GOOGL": 0.4},
        ...     rebalance_frequency=30
        ... )
        >>>
        >>> # Create time series data
        >>> dates = pd.date_range("2024-01-01", periods=100, freq="D")
        >>> timeseries_data = {
        ...     "AAPL": TimeSeries(...),
        ...     "GOOGL": TimeSeries(...),
        ... }
        >>>
        >>> # Run backtest
        >>> backtest = run_portfolio_backtest(
        ...     strategy=strategy,
        ...     timeseries_data=timeseries_data,
        ...     initial_capital=100000.0,
        ...     commission=0.001,
        ...     slippage=0.001
        ... )
        >>>
        >>> print(f"Total Return: {backtest.total_return():.2f}%")
        >>> print(f"Final Equity: ${backtest.final_equity():,.2f}")
    """
    # Use default engine if none provided
    if engine is None:
        engine = PortfolioBacktestEngine()

    # Run the backtest
    backtest = engine.run(
        strategy=strategy,
        timeseries_data=timeseries_data,
        initial_capital=initial_capital,
        commission=commission,
        slippage=slippage,
    )

    return backtest
