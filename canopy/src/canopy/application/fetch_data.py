"""
Fetch Data Use Case - Application layer for data fetching.

This use case demonstrates how to use data providers to fetch market data.
It follows the Hexagonal Architecture pattern by depending on the port (interface)
rather than concrete implementations.
"""
from canopy.ports.data_provider import IDataProvider
from canopy.domain.timeseries import TimeSeries


class FetchDataUseCase:
    """
    Use case for fetching market data.

    This class demonstrates dependency injection - it depends on the IDataProvider
    interface, not on concrete implementations like CSVDataProvider or YahooFinanceProvider.
    """

    def __init__(self, data_provider: IDataProvider):
        """
        Initialize the use case with a data provider.

        Args:
            data_provider: Data provider implementation (CSV, Yahoo, etc.)
        """
        self.data_provider = data_provider

    def execute(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        interval: str = "1d"
    ) -> TimeSeries:
        """
        Fetch OHLCV data for a symbol.

        Args:
            symbol: Ticker symbol (e.g., "SPY", "AAPL")
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Data interval (default: "1d")

        Returns:
            TimeSeries with OHLCV data

        Raises:
            ValueError: If inputs are invalid
            RuntimeError: If data cannot be fetched
        """
        # Validate symbol first
        if not self.data_provider.validate_symbol(symbol):
            raise ValueError(f"Invalid or unavailable symbol: {symbol}")

        # Fetch data
        timeseries = self.data_provider.get_ohlcv(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            interval=interval
        )

        # Validate data quality
        if len(timeseries) == 0:
            raise RuntimeError(
                f"No data returned for {symbol} from {start_date} to {end_date}"
            )

        return timeseries

    def validate_symbol(self, symbol: str) -> bool:
        """
        Check if a symbol is valid.

        Args:
            symbol: Ticker symbol

        Returns:
            True if symbol is valid, False otherwise
        """
        return self.data_provider.validate_symbol(symbol)


# Example usage (for documentation):
"""
Example: Fetch data using CSV provider
---------------------------------------

from canopy.adapters.data.provider_factory import DataProviderFactory
from canopy.application.fetch_data import FetchDataUseCase

# Create provider using factory
provider = DataProviderFactory.create("csv", data_dir="/path/to/data")

# Create use case with provider
use_case = FetchDataUseCase(data_provider=provider)

# Fetch data
timeseries = use_case.execute(
    symbol="SPY",
    start_date="2020-01-01",
    end_date="2020-12-31"
)

print(f"Fetched {len(timeseries)} data points")
print(f"First close: {timeseries.close.iloc[0]}")
print(f"Last close: {timeseries.close.iloc[-1]}")


Example: Fetch data using Yahoo Finance
----------------------------------------

from canopy.adapters.data.provider_factory import DataProviderFactory
from canopy.application.fetch_data import FetchDataUseCase

# Create provider using factory
provider = DataProviderFactory.create("yahoo")

# Create use case with provider
use_case = FetchDataUseCase(data_provider=provider)

# Fetch data
timeseries = use_case.execute(
    symbol="AAPL",
    start_date="2020-01-01",
    end_date="2020-12-31"
)

print(f"Fetched {len(timeseries)} data points for AAPL")


Example: Easy provider switching
---------------------------------

def run_analysis(provider_type: str, **kwargs):
    '''Run analysis with any data provider'''
    # Create provider
    provider = DataProviderFactory.create(provider_type, **kwargs)
    
    # Create use case
    use_case = FetchDataUseCase(data_provider=provider)
    
    # Fetch data
    timeseries = use_case.execute(
        symbol="SPY",
        start_date="2020-01-01",
        end_date="2020-12-31"
    )
    
    # Run analysis
    print(f"Average close: {timeseries.close.mean()}")

# Use CSV data for testing
run_analysis("csv", data_dir="/path/to/test/data")

# Use Yahoo Finance for production
run_analysis("yahoo")
"""
