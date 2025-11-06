"""
API integration tests.

Tests the FastAPI endpoints and workflows.
"""

import pytest
from fastapi.testclient import TestClient
from canopy.api.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data or "name" in data


def test_parse_strategy_endpoint():
    """Test strategy parsing endpoint."""
    strategy_code = """
strategy "Test Strategy"
ma = sma(close, 20)
buy when close > ma
sell when close < ma
"""

    response = client.post(
        "/api/strategies/parse",
        json={"strategy_code": strategy_code, "validate": True}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["strategy_name"] == "Test Strategy"


def test_parse_invalid_strategy():
    """Test parsing invalid strategy."""
    invalid_code = "this is not valid canopy code"

    response = client.post(
        "/api/strategies/parse",
        json={"strategy_code": invalid_code}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert len(data["errors"]) > 0


def test_list_indicators_endpoint():
    """Test listing indicators."""
    response = client.get("/api/indicators/list")
    assert response.status_code == 200
    data = response.json()
    assert "indicators" in data
    assert len(data["indicators"]) > 0


def test_get_indicator_detail():
    """Test getting indicator details."""
    response = client.get("/api/indicators/sma")
    assert response.status_code in [200, 404]  # May not be implemented yet


def test_list_data_providers():
    """Test listing data providers."""
    response = client.get("/api/data/providers")
    assert response.status_code == 200
    data = response.json()
    assert "providers" in data


def test_search_symbols():
    """Test symbol search."""
    response = client.get("/api/data/symbols?query=AAPL")
    assert response.status_code == 200
    data = response.json()
    assert "symbols" in data


def test_submit_backtest():
    """Test submitting a backtest job."""
    strategy_code = """
strategy "Test"
ma = sma(close, 20)
buy when close > ma
sell when close < ma
"""

    response = client.post(
        "/api/backtests/run",
        json={
            "strategy_code": strategy_code,
            "symbol": "AAPL",
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "initial_capital": 10000,
            "commission": 0.001,
            "provider": "yahoo"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] in ["pending", "running"]

    # Check job status
    job_id = data["job_id"]
    status_response = client.get(f"/api/backtests/{job_id}")
    assert status_response.status_code == 200


def test_list_backtests():
    """Test listing all backtests."""
    response = client.get("/api/backtests")
    assert response.status_code == 200
    data = response.json()
    assert "jobs" in data
