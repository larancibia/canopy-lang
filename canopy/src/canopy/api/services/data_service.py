"""
Data Service - Business logic for data operations.
"""

from datetime import datetime
from typing import List, Dict, Any
from canopy.ports.data_provider import IDataProvider
from canopy.domain.timeseries import TimeSeries
from canopy.adapters.data.provider_factory import DataProviderFactory


class DataService:
    """Service for handling data-related operations."""

    def __init__(self, data_provider: IDataProvider = None):
        """
        Initialize the data service.

        Args:
            data_provider: Data provider instance (defaults to Yahoo)
        """
        self.provider = data_provider or DataProviderFactory.create("yahoo")

    def get_ohlcv_data(
        self, symbol: str, start_date: datetime, end_date: datetime
    ) -> TimeSeries:
        """
        Fetch OHLCV data for a symbol.

        Args:
            symbol: Trading symbol
            start_date: Start date
            end_date: End date

        Returns:
            TimeSeries with OHLCV data

        Raises:
            Exception: If data fetch fails
        """
        return self.provider.fetch_ohlcv(symbol, start_date, end_date)

    def timeseries_to_dict(self, ts: TimeSeries) -> List[Dict[str, Any]]:
        """
        Convert TimeSeries to list of dictionaries.

        Args:
            ts: TimeSeries instance

        Returns:
            List of OHLCV data points as dictionaries
        """
        data = []
        for i in range(len(ts.close)):
            data.append(
                {
                    "timestamp": ts.close.index[i].isoformat(),
                    "open": float(ts.open.iloc[i]),
                    "high": float(ts.high.iloc[i]),
                    "low": float(ts.low.iloc[i]),
                    "close": float(ts.close.iloc[i]),
                    "volume": float(ts.volume.iloc[i]),
                }
            )
        return data

    def get_available_providers(self) -> List[str]:
        """
        Get list of available data providers.

        Returns:
            List of provider names
        """
        return DataProviderFactory.get_available_providers()

    def search_symbols(self, query: str) -> List[str]:
        """
        Search for trading symbols.

        Note: For MVP, this is a simple mock implementation.
        In production, this would query a symbols database or API.

        Args:
            query: Search query

        Returns:
            List of matching symbols
        """
        # Mock implementation - returns common symbols matching query
        all_symbols = [
            "AAPL",
            "MSFT",
            "GOOGL",
            "AMZN",
            "TSLA",
            "META",
            "NVDA",
            "AMD",
            "NFLX",
            "DIS",
            "BA",
            "GE",
            "IBM",
            "INTC",
            "JPM",
            "BAC",
            "WMT",
            "XOM",
            "CVX",
            "PFE",
        ]

        query = query.upper()
        matches = [s for s in all_symbols if query in s]
        return matches[:10]  # Return max 10 results
