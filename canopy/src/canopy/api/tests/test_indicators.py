"""
Tests for indicator endpoints.
"""

import pytest
from fastapi.testclient import TestClient


def test_list_indicators(client: TestClient):
    """Test listing all indicators."""
    response = client.get("/api/indicators")

    assert response.status_code == 200
    data = response.json()
    assert "indicators" in data
    assert "count" in data
    assert len(data["indicators"]) > 0
    assert "SMA" in data["indicators"]
    assert "EMA" in data["indicators"]
    assert "RSI" in data["indicators"]


def test_get_indicator_info_sma(client: TestClient):
    """Test getting SMA indicator info."""
    response = client.get("/api/indicators/sma")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "SMA"
    assert "description" in data
    assert "parameters" in data
    assert "example" in data


def test_get_indicator_info_ema(client: TestClient):
    """Test getting EMA indicator info."""
    response = client.get("/api/indicators/ema")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "EMA"


def test_get_indicator_info_rsi(client: TestClient):
    """Test getting RSI indicator info."""
    response = client.get("/api/indicators/rsi")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "RSI"


def test_get_nonexistent_indicator(client: TestClient):
    """Test getting non-existent indicator."""
    response = client.get("/api/indicators/nonexistent")

    assert response.status_code == 404


def test_calculate_sma(client: TestClient):
    """Test calculating SMA indicator."""
    response = client.post(
        "/api/indicators/sma/calculate",
        json={"data": [100, 102, 101, 105, 107, 106, 108, 110, 109, 111], "params": {"period": 5}},
    )

    assert response.status_code == 200
    data = response.json()
    assert "indicator" in data
    assert data["indicator"] == "SMA"
    assert "values" in data
    assert "count" in data
    assert len(data["values"]) == 10
    # First 4 values should be None (not enough data for period=5)
    assert data["values"][:4] == [None, None, None, None]
    # 5th value should be the average of first 5 values
    assert data["values"][4] is not None


def test_calculate_ema(client: TestClient):
    """Test calculating EMA indicator."""
    response = client.post(
        "/api/indicators/ema/calculate",
        json={"data": [100, 102, 101, 105, 107, 106, 108, 110, 109, 111], "params": {"period": 5}},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["indicator"] == "EMA"
    assert len(data["values"]) == 10


def test_calculate_rsi(client: TestClient):
    """Test calculating RSI indicator."""
    response = client.post(
        "/api/indicators/rsi/calculate",
        json={"data": [100, 102, 101, 105, 107, 106, 108, 110, 109, 111, 113, 112, 115, 117, 116], "params": {"period": 14}},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["indicator"] == "RSI"
    assert len(data["values"]) == 15


def test_calculate_rsi_default_period(client: TestClient):
    """Test calculating RSI with default period."""
    response = client.post(
        "/api/indicators/rsi/calculate",
        json={"data": [100, 102, 101, 105, 107, 106, 108, 110, 109, 111, 113, 112, 115, 117, 116], "params": {}},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["indicator"] == "RSI"
    # Either params are empty or contain default period
    assert isinstance(data["parameters"], dict)


def test_calculate_indicator_missing_period(client: TestClient):
    """Test calculating indicator without required period."""
    response = client.post(
        "/api/indicators/sma/calculate",
        json={"data": [100, 102, 101, 105, 107], "params": {}},
    )

    assert response.status_code == 400  # Bad request


def test_calculate_indicator_invalid_data(client: TestClient):
    """Test calculating indicator with invalid data."""
    response = client.post(
        "/api/indicators/sma/calculate",
        json={"data": "invalid", "params": {"period": 5}},
    )

    assert response.status_code == 422  # Validation error


def test_calculate_nonexistent_indicator(client: TestClient):
    """Test calculating non-existent indicator."""
    response = client.post(
        "/api/indicators/nonexistent/calculate",
        json={"data": [100, 102, 101, 105, 107], "params": {"period": 5}},
    )

    assert response.status_code == 404


def test_calculate_indicator_empty_data(client: TestClient):
    """Test calculating indicator with empty data."""
    response = client.post(
        "/api/indicators/sma/calculate", json={"data": [], "params": {"period": 5}}
    )

    assert response.status_code in [200, 400]  # Might handle gracefully or error
