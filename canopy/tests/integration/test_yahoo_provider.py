"""
Integration tests for Yahoo Finance Data Provider.

Following TDD: These tests are written FIRST, before implementation.
They will initially FAIL (RED), then we implement to make them PASS (GREEN).

Note: These are integration tests that require network access.
"""
import pytest
import pandas as pd
from canopy.adapters.data.yahoo_provider import YahooFinanceProvider
from canopy.domain.timeseries import TimeSeries


@pytest.fixture
def yahoo_provider():
    """Create a Yahoo Finance provider instance"""
    return YahooFinanceProvider()


@pytest.mark.integration
def test_yahoo_provider_fetches_data(yahoo_provider):
    """
    Yahoo Finance provider should fetch real OHLCV data.

    This test requires network access and will make a real API call.
    """
    # Act
    timeseries = yahoo_provider.get_ohlcv(
        symbol="SPY",
        start_date="2020-01-02",
        end_date="2020-01-10"
    )

    # Assert
    assert isinstance(timeseries, TimeSeries)
    assert len(timeseries) > 0
    # Verify we have data in the expected range
    assert timeseries.index[0].year == 2020
    assert timeseries.index[0].month == 1


@pytest.mark.integration
def test_yahoo_provider_validates_symbol(yahoo_provider):
    """
    Yahoo Finance provider should validate if symbol exists.
    """
    # Assert - SPY should be valid
    assert yahoo_provider.validate_symbol("SPY") is True

    # Invalid symbol should return False
    assert yahoo_provider.validate_symbol("INVALIDXYZ123") is False


@pytest.mark.integration
def test_yahoo_provider_handles_invalid_symbol(yahoo_provider):
    """
    Yahoo Finance provider should raise error for invalid symbols.
    """
    # Act & Assert
    with pytest.raises(RuntimeError, match="Failed to fetch data"):
        yahoo_provider.get_ohlcv(
            symbol="INVALIDXYZ123",
            start_date="2020-01-02",
            end_date="2020-01-10"
        )


def test_yahoo_provider_handles_invalid_dates(yahoo_provider):
    """
    Yahoo Finance provider should raise error for invalid date formats.
    """
    # Act & Assert
    with pytest.raises(ValueError, match="Invalid date format"):
        yahoo_provider.get_ohlcv(
            symbol="SPY",
            start_date="not-a-date",
            end_date="2020-01-10"
        )


@pytest.mark.integration
def test_yahoo_provider_respects_date_range(yahoo_provider):
    """
    Yahoo Finance provider should only return data in the requested date range.
    """
    # Act
    timeseries = yahoo_provider.get_ohlcv(
        symbol="SPY",
        start_date="2020-02-03",
        end_date="2020-02-07"
    )

    # Assert
    assert len(timeseries) > 0
    # First date should be on or after start date
    assert timeseries.index[0] >= pd.Timestamp("2020-02-03")
    # Last date should be on or before end date
    assert timeseries.index[-1] <= pd.Timestamp("2020-02-07")


@pytest.mark.integration
def test_yahoo_provider_returns_all_ohlcv_fields(yahoo_provider):
    """
    Yahoo Finance provider should return all OHLCV fields.
    """
    # Act
    timeseries = yahoo_provider.get_ohlcv(
        symbol="SPY",
        start_date="2020-01-02",
        end_date="2020-01-02"
    )

    # Assert - Check all fields are present and non-null
    assert len(timeseries) > 0
    assert not timeseries.open.isna().all()
    assert not timeseries.high.isna().all()
    assert not timeseries.low.isna().all()
    assert not timeseries.close.isna().all()
    assert not timeseries.volume.isna().all()


@pytest.mark.integration
def test_yahoo_provider_parses_dates_as_datetime(yahoo_provider):
    """
    Yahoo Finance provider should parse dates as pandas datetime objects.
    """
    # Act
    timeseries = yahoo_provider.get_ohlcv(
        symbol="SPY",
        start_date="2020-01-02",
        end_date="2020-01-02"
    )

    # Assert
    assert isinstance(timeseries.index, pd.DatetimeIndex)


def test_yahoo_provider_handles_reversed_dates(yahoo_provider):
    """
    Yahoo Finance provider should raise error when start date is after end date.
    """
    # Act & Assert
    with pytest.raises(ValueError, match="Start date must be before end date"):
        yahoo_provider.get_ohlcv(
            symbol="SPY",
            start_date="2020-12-31",
            end_date="2020-01-01"
        )


@pytest.mark.integration
def test_yahoo_provider_handles_future_dates(yahoo_provider):
    """
    Yahoo Finance provider should handle future dates gracefully.
    """
    # Act
    timeseries = yahoo_provider.get_ohlcv(
        symbol="SPY",
        start_date="2025-01-01",
        end_date="2025-12-31"
    )

    # Assert - Should return empty or minimal data for future dates
    # Yahoo Finance typically returns empty data for future dates
    assert isinstance(timeseries, TimeSeries)
