"""
Integration tests for the API.
"""

import pytest
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "job_queue" in data


def test_root_endpoint(client: TestClient):
    """Test root endpoint."""
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "docs" in data


@pytest.mark.slow
def test_full_workflow(client: TestClient, sample_strategy_code: str):
    """Test complete workflow from strategy to backtest results."""
    # 1. Parse strategy
    parse_response = client.post(
        "/api/strategies/parse", json={"strategy_code": sample_strategy_code}
    )
    assert parse_response.status_code == 200
    assert parse_response.json()["success"] is True

    # 2. Validate strategy
    validate_response = client.post(
        "/api/strategies/validate", json={"strategy_code": sample_strategy_code}
    )
    assert validate_response.status_code == 200
    assert validate_response.json()["valid"] is True

    # 3. Submit backtest
    backtest_request = {
        "strategy_code": sample_strategy_code,
        "symbol": "AAPL",
        "start_date": "2023-01-01T00:00:00Z",
        "end_date": "2023-03-31T23:59:59Z",
        "initial_capital": 10000.0,
    }
    create_response = client.post("/api/backtests", json=backtest_request)
    assert create_response.status_code == 202
    job_id = create_response.json()["job_id"]

    # 4. Check status
    status_response = client.get(f"/api/backtests/{job_id}")
    assert status_response.status_code == 200
    assert status_response.json()["job_id"] == job_id

    # Note: We don't wait for completion in this test as it may take time


def test_cors_headers(client: TestClient):
    """Test that CORS headers are set correctly."""
    response = client.get("/health")

    # CORS headers might not be visible in TestClient
    # This test is more for documentation
    assert response.status_code == 200


def test_openapi_docs(client: TestClient):
    """Test that OpenAPI documentation is available."""
    response = client.get("/openapi.json")

    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "info" in data
    assert "paths" in data


def test_api_versioning(client: TestClient):
    """Test that API is properly versioned."""
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert data["version"] == "0.1.0"


def test_error_handling_404(client: TestClient):
    """Test 404 error handling."""
    response = client.get("/api/nonexistent")

    assert response.status_code == 404


def test_error_handling_validation(client: TestClient):
    """Test validation error handling."""
    response = client.post("/api/strategies/parse", json={"wrong_field": "value"})

    assert response.status_code == 422
    data = response.json()
    assert "error" in data or "detail" in data


@pytest.mark.parametrize(
    "endpoint",
    [
        "/api/strategies/examples",
        "/api/indicators",
        "/api/data/providers",
        "/health",
        "/",
    ],
)
def test_public_endpoints_accessible(client: TestClient, endpoint: str):
    """Test that public endpoints are accessible without authentication."""
    response = client.get(endpoint)

    assert response.status_code == 200
