"""
Integration tests for CSV Data Provider.

Following TDD: These tests are written FIRST, before implementation.
They will initially FAIL (RED), then we implement to make them PASS (GREEN).
"""
import pytest
import pandas as pd
from pathlib import Path
from canopy.adapters.data.csv_provider import CSVDataProvider
from canopy.domain.timeseries import TimeSeries


# Fixture to get the test data directory
@pytest.fixture
def fixtures_dir():
    """Get the fixtures directory path"""
    return Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def csv_provider(fixtures_dir):
    """Create a CSV provider instance"""
    return CSVDataProvider(data_dir=fixtures_dir)


def test_csv_provider_loads_data(csv_provider):
    """
    CSV provider should load OHLCV data from a CSV file.

    This is the happy path test - loading valid data.
    """
    # Act
    timeseries = csv_provider.get_ohlcv(
        symbol="SPY",
        start_date="2020-01-02",
        end_date="2020-01-10"
    )

    # Assert
    assert isinstance(timeseries, TimeSeries)
    assert len(timeseries) == 7  # 7 trading days from Jan 2 to Jan 10 (2,3,6,7,8,9,10)
    assert timeseries.close.iloc[0] == 325.12  # First close price
    assert timeseries.close.iloc[-1] == 328.77  # Last close price


def test_csv_provider_validates_csv_format(fixtures_dir):
    """
    CSV provider should validate that CSV has required columns.

    Expected columns: Date, Open, High, Low, Close, Volume
    """
    # Arrange
    provider = CSVDataProvider(data_dir=fixtures_dir)

    # Act & Assert
    with pytest.raises(ValueError, match="Missing required columns"):
        provider.get_ohlcv(
            symbol="INVALID",  # This CSV is missing Volume column
            start_date="2020-01-02",
            end_date="2020-01-03"
        )


def test_csv_provider_handles_missing_file(csv_provider):
    """
    CSV provider should raise an error when CSV file doesn't exist.
    """
    # Act & Assert
    with pytest.raises(FileNotFoundError, match="CSV file not found"):
        csv_provider.get_ohlcv(
            symbol="NONEXISTENT",
            start_date="2020-01-02",
            end_date="2020-01-10"
        )


def test_csv_provider_handles_invalid_dates(csv_provider):
    """
    CSV provider should raise an error for invalid date formats.
    """
    # Act & Assert
    with pytest.raises(ValueError, match="Invalid date format"):
        csv_provider.get_ohlcv(
            symbol="SPY",
            start_date="not-a-date",
            end_date="2020-01-10"
        )


def test_csv_provider_filters_by_date_range(csv_provider):
    """
    CSV provider should filter data to only include the requested date range.
    """
    # Act
    timeseries = csv_provider.get_ohlcv(
        symbol="SPY",
        start_date="2020-02-03",
        end_date="2020-02-07"
    )

    # Assert
    assert len(timeseries) == 5  # 5 trading days
    # Check first and last dates
    assert timeseries.index[0].strftime("%Y-%m-%d") == "2020-02-03"
    assert timeseries.index[-1].strftime("%Y-%m-%d") == "2020-02-07"


def test_csv_provider_returns_all_ohlcv_fields(csv_provider):
    """
    CSV provider should return all OHLCV fields correctly.
    """
    # Act
    timeseries = csv_provider.get_ohlcv(
        symbol="SPY",
        start_date="2020-01-02",
        end_date="2020-01-02"
    )

    # Assert - Check first row matches CSV exactly
    assert timeseries.open.iloc[0] == 324.87
    assert timeseries.high.iloc[0] == 325.38
    assert timeseries.low.iloc[0] == 323.34
    assert timeseries.close.iloc[0] == 325.12
    assert timeseries.volume.iloc[0] == 75658900


def test_csv_provider_validates_symbol(csv_provider, fixtures_dir):
    """
    CSV provider should validate if symbol CSV file exists.
    """
    # Assert
    assert csv_provider.validate_symbol("SPY") is True
    assert csv_provider.validate_symbol("NONEXISTENT") is False


def test_csv_provider_handles_empty_date_range(csv_provider):
    """
    CSV provider should raise an error when date range contains no data.
    """
    # Act & Assert
    with pytest.raises(ValueError, match="No data found for date range"):
        csv_provider.get_ohlcv(
            symbol="SPY",
            start_date="2019-01-01",  # Before our data starts
            end_date="2019-01-31"
        )


def test_csv_provider_sorts_by_date(csv_provider):
    """
    CSV provider should ensure data is sorted by date ascending.
    """
    # Act
    timeseries = csv_provider.get_ohlcv(
        symbol="SPY",
        start_date="2020-01-02",
        end_date="2020-01-10"
    )

    # Assert - dates should be ascending
    dates = timeseries.index
    assert all(dates[i] <= dates[i + 1] for i in range(len(dates) - 1))


def test_csv_provider_parses_dates_as_datetime(csv_provider):
    """
    CSV provider should parse dates as pandas datetime objects.
    """
    # Act
    timeseries = csv_provider.get_ohlcv(
        symbol="SPY",
        start_date="2020-01-02",
        end_date="2020-01-02"
    )

    # Assert
    assert isinstance(timeseries.index, pd.DatetimeIndex)
    assert timeseries.index[0].year == 2020
    assert timeseries.index[0].month == 1
    assert timeseries.index[0].day == 2


def test_csv_provider_handles_different_csv_naming(fixtures_dir):
    """
    CSV provider should support different CSV naming conventions.
    Should look for: SYMBOL.csv or SYMBOL_1d.csv
    """
    # This test verifies the CSV file discovery logic
    provider = CSVDataProvider(data_dir=fixtures_dir)

    # Should find SPY.csv
    assert provider.validate_symbol("SPY") is True

    # Create a test CSV with interval suffix
    test_csv = fixtures_dir / "TEST_1d.csv"
    test_csv.write_text("Date,Open,High,Low,Close,Volume\n2020-01-02,100,101,99,100.5,1000000\n")

    # Should find TEST_1d.csv
    assert provider.validate_symbol("TEST") is True

    # Cleanup
    test_csv.unlink()
