"""
Data Provider Port (Interface) - Hexagonal Architecture.

This port defines the contract for data providers without specifying implementation.
Different adapters (CSV, Yahoo Finance, Alpaca, etc.) will implement this interface.
"""
from abc import ABC, abstractmethod
from canopy.domain.timeseries import TimeSeries


class IDataProvider(ABC):
    """
    Port (interface) for data providers.

    This interface defines the contract that all data provider adapters must implement.
    It follows the Dependency Inversion Principle - the domain depends on this abstraction,
    not on concrete implementations.
    """

    @abstractmethod
    def get_ohlcv(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        interval: str = "1d"
    ) -> TimeSeries:
        """
        Fetch OHLCV data for a given symbol and date range.

        Args:
            symbol: Ticker symbol (e.g., "SPY", "AAPL")
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            interval: Data interval (e.g., "1d", "1h", "5m")

        Returns:
            TimeSeries object containing OHLCV data

        Raises:
            ValueError: If symbol is invalid or date range is invalid
            RuntimeError: If data cannot be fetched (network error, etc.)
        """
        pass

    @abstractmethod
    def validate_symbol(self, symbol: str) -> bool:
        """
        Check if a symbol is valid and data is available.

        Args:
            symbol: Ticker symbol to validate

        Returns:
            True if symbol is valid and data is available, False otherwise
        """
        pass
