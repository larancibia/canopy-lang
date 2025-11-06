"""
Unit tests for Data Provider Factory.

Following TDD: These tests are written FIRST, before implementation.
They will initially FAIL (RED), then we implement to make them PASS (GREEN).
"""
import pytest
from pathlib import Path
from canopy.adapters.data.provider_factory import DataProviderFactory
from canopy.adapters.data.csv_provider import CSVDataProvider
from canopy.adapters.data.yahoo_provider import YahooFinanceProvider
from canopy.ports.data_provider import IDataProvider


def test_factory_creates_csv_provider():
    """
    Factory should create a CSV data provider when given 'csv' type.
    """
    # Arrange
    data_dir = Path("/tmp/test_data")
    data_dir.mkdir(exist_ok=True)

    # Act
    provider = DataProviderFactory.create("csv", data_dir=data_dir)

    # Assert
    assert isinstance(provider, CSVDataProvider)
    assert isinstance(provider, IDataProvider)


def test_factory_creates_yahoo_provider():
    """
    Factory should create a Yahoo Finance provider when given 'yahoo' type.
    """
    # Act
    provider = DataProviderFactory.create("yahoo")

    # Assert
    assert isinstance(provider, YahooFinanceProvider)
    assert isinstance(provider, IDataProvider)


def test_factory_raises_for_unknown_type():
    """
    Factory should raise ValueError for unknown provider types.
    """
    # Act & Assert
    with pytest.raises(ValueError, match="Unknown provider type"):
        DataProviderFactory.create("unknown_provider")


def test_factory_raises_when_csv_missing_data_dir():
    """
    Factory should raise ValueError when creating CSV provider without data_dir.
    """
    # Act & Assert
    with pytest.raises(ValueError, match="csv provider requires data_dir"):
        DataProviderFactory.create("csv")


def test_factory_csv_provider_validates_data_dir():
    """
    Factory should create CSV provider that validates data_dir exists.
    """
    # Act & Assert - nonexistent directory should raise error
    with pytest.raises(ValueError, match="Data directory does not exist"):
        DataProviderFactory.create("csv", data_dir="/nonexistent/directory/path")


def test_factory_supports_case_insensitive_types():
    """
    Factory should support case-insensitive provider types.
    """
    # Arrange
    data_dir = Path("/tmp/test_data")
    data_dir.mkdir(exist_ok=True)

    # Act & Assert
    provider1 = DataProviderFactory.create("CSV", data_dir=data_dir)
    assert isinstance(provider1, CSVDataProvider)

    provider2 = DataProviderFactory.create("YAHOO")
    assert isinstance(provider2, YahooFinanceProvider)

    provider3 = DataProviderFactory.create("Yahoo")
    assert isinstance(provider3, YahooFinanceProvider)


def test_factory_get_available_providers():
    """
    Factory should provide a list of available provider types.
    """
    # Act
    providers = DataProviderFactory.get_available_providers()

    # Assert
    assert isinstance(providers, list)
    assert "csv" in providers
    assert "yahoo" in providers
    assert len(providers) >= 2
