"""
Portfolio Backtest Engine Port - Interface for portfolio backtest execution.

This module defines the port (interface) for portfolio backtest engines following
hexagonal architecture. Adapters will implement this interface.
"""

from abc import ABC, abstractmethod
from typing import Dict
from canopy.domain.portfolio_strategy import PortfolioStrategy
from canopy.domain.timeseries import TimeSeries
from canopy.domain.backtest import Backtest


class IPortfolioBacktestEngine(ABC):
    """
    Port for portfolio backtest engines.

    This interface defines the contract that all portfolio backtest engine
    adapters must implement. It allows the application to swap different
    backtest implementations without changing business logic.
    """

    @abstractmethod
    def run(
        self,
        strategy: PortfolioStrategy,
        timeseries_data: Dict[str, TimeSeries],
        initial_capital: float = 100000.0,
        commission: float = 0.0,
        slippage: float = 0.0,
    ) -> Backtest:
        """
        Run a portfolio backtest on the given strategy and data.

        Args:
            strategy: Portfolio strategy to backtest
            timeseries_data: Dictionary mapping symbol to TimeSeries data
            initial_capital: Starting capital (default $100,000)
            commission: Commission per trade as a percentage (e.g., 0.001 for 0.1%)
            slippage: Slippage per trade as a percentage (e.g., 0.001 for 0.1%)

        Returns:
            Backtest object containing results

        Raises:
            ValueError: If inputs are invalid
        """
        pass
