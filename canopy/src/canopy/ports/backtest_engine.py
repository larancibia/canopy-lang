"""
Backtest Engine Port - Interface for backtest execution engines.

This module defines the port (interface) for backtest engines following
hexagonal architecture. Adapters will implement this interface.
"""

from abc import ABC, abstractmethod
from canopy.domain.strategy import Strategy
from canopy.domain.timeseries import TimeSeries
from canopy.domain.backtest import Backtest


class IBacktestEngine(ABC):
    """
    Port for backtest engines.

    This interface defines the contract that all backtest engine adapters
    must implement. It allows the application to swap different backtest
    implementations without changing business logic.
    """

    @abstractmethod
    def run(
        self,
        strategy: Strategy,
        timeseries: TimeSeries,
        initial_capital: float = 10000.0,
        commission: float = 0.0,
        slippage: float = 0.0
    ) -> Backtest:
        """
        Run a backtest on the given strategy and data.

        Args:
            strategy: Strategy to backtest
            timeseries: Historical OHLCV data
            initial_capital: Starting capital (default $10,000)
            commission: Commission per trade as a percentage (e.g., 0.001 for 0.1%)
            slippage: Slippage per trade as a percentage (e.g., 0.001 for 0.1%)

        Returns:
            Backtest object containing results

        Raises:
            ValueError: If inputs are invalid
        """
        pass
