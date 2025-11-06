"""
Tests for data endpoints.
"""

import pytest
from fastapi.testclient import TestClient


def test_get_providers(client: TestClient):
    """Test getting available data providers."""
    response = client.get("/api/data/providers")

    assert response.status_code == 200
    data = response.json()
    assert "providers" in data
    assert "default" in data
    assert isinstance(data["providers"], list)
    assert len(data["providers"]) > 0
    assert "yahoo" in data["providers"]


def test_search_symbols(client: TestClient):
    """Test searching for symbols."""
    response = client.get("/api/data/symbols?q=AAPL")

    assert response.status_code == 200
    data = response.json()
    assert "query" in data
    assert "results" in data
    assert "count" in data
    assert data["query"] == "AAPL"
    assert "AAPL" in data["results"]


def test_search_symbols_partial_match(client: TestClient):
    """Test searching with partial match."""
    response = client.get("/api/data/symbols?q=AA")

    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) > 0


def test_search_symbols_no_results(client: TestClient):
    """Test searching with no results."""
    response = client.get("/api/data/symbols?q=ZZZZZZZ")

    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 0


def test_search_symbols_missing_query(client: TestClient):
    """Test searching without query parameter."""
    response = client.get("/api/data/symbols")

    assert response.status_code == 422  # Validation error


@pytest.mark.slow
def test_get_ohlcv_data(client: TestClient):
    """Test getting OHLCV data."""
    response = client.get(
        "/api/data/AAPL/ohlcv",
        params={
            "start_date": "2023-01-01T00:00:00Z",
            "end_date": "2023-01-31T23:59:59Z",
        },
    )

    # May fail if network/API issues
    if response.status_code != 200:
        pytest.skip("Data fetch failed (likely network/API issue)")

    data = response.json()
    assert data["symbol"] == "AAPL"
    assert "data" in data
    assert "count" in data
    assert len(data["data"]) > 0

    # Check data structure
    first_point = data["data"][0]
    assert "timestamp" in first_point
    assert "open" in first_point
    assert "high" in first_point
    assert "low" in first_point
    assert "close" in first_point
    assert "volume" in first_point


def test_get_ohlcv_invalid_symbol(client: TestClient):
    """Test getting data for invalid symbol."""
    response = client.get(
        "/api/data/INVALID_SYMBOL_XYZ/ohlcv",
        params={
            "start_date": "2023-01-01T00:00:00Z",
            "end_date": "2023-01-31T23:59:59Z",
        },
    )

    # Should return 400 or handle gracefully
    assert response.status_code in [400, 404]


def test_get_ohlcv_missing_dates(client: TestClient):
    """Test getting OHLCV without dates."""
    response = client.get("/api/data/AAPL/ohlcv")

    assert response.status_code == 422  # Validation error


def test_get_ohlcv_invalid_date_format(client: TestClient):
    """Test getting OHLCV with invalid date format."""
    response = client.get(
        "/api/data/AAPL/ohlcv",
        params={"start_date": "invalid", "end_date": "2023-01-31T23:59:59Z"},
    )

    assert response.status_code == 422  # Validation error
