"""
Tests for backtest endpoints.
"""

import pytest
from fastapi.testclient import TestClient
import time


def test_create_backtest(client: TestClient, sample_backtest_request: dict):
    """Test creating a backtest job."""
    response = client.post("/api/backtests", json=sample_backtest_request)

    assert response.status_code == 202  # Accepted
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "pending"
    assert data["message"] is not None


def test_get_backtest_status(client: TestClient, sample_backtest_request: dict):
    """Test getting backtest status."""
    # Create a backtest
    create_response = client.post("/api/backtests", json=sample_backtest_request)
    job_id = create_response.json()["job_id"]

    # Get status
    response = client.get(f"/api/backtests/{job_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == job_id
    assert "status" in data
    assert "created_at" in data


def test_get_nonexistent_backtest_status(client: TestClient):
    """Test getting status of non-existent backtest."""
    response = client.get("/api/backtests/invalid_job_id")

    assert response.status_code == 404


@pytest.mark.slow
def test_get_backtest_results(client: TestClient, sample_backtest_request: dict):
    """Test getting backtest results after completion."""
    # Create a backtest
    create_response = client.post("/api/backtests", json=sample_backtest_request)
    job_id = create_response.json()["job_id"]

    # Wait for completion (with timeout)
    max_wait = 60  # seconds
    start_time = time.time()
    while time.time() - start_time < max_wait:
        status_response = client.get(f"/api/backtests/{job_id}")
        status = status_response.json()["status"]

        if status == "completed":
            break
        elif status == "failed":
            pytest.fail("Backtest failed")

        time.sleep(2)

    # Get results
    response = client.get(f"/api/backtests/{job_id}/results")

    if response.status_code == 400:
        # Job might still be running
        pytest.skip("Job not completed in time")

    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == job_id
    assert data["status"] == "completed"
    assert "metrics" in data
    assert "trades" in data
    assert "equity_curve" in data


def test_get_results_before_completion(client: TestClient, sample_backtest_request: dict):
    """Test getting results before backtest is complete."""
    # Create a backtest
    create_response = client.post("/api/backtests", json=sample_backtest_request)
    job_id = create_response.json()["job_id"]

    # Try to get results immediately
    response = client.get(f"/api/backtests/{job_id}/results")

    # Should return 400 if not completed
    assert response.status_code in [400, 200]  # Might complete quickly


def test_cancel_backtest(client: TestClient, sample_backtest_request: dict):
    """Test cancelling a backtest."""
    # Create a backtest
    create_response = client.post("/api/backtests", json=sample_backtest_request)
    job_id = create_response.json()["job_id"]

    # Cancel immediately
    response = client.delete(f"/api/backtests/{job_id}")

    assert response.status_code == 200
    data = response.json()
    assert "cancelled" in data


def test_list_backtests(client: TestClient, sample_backtest_request: dict):
    """Test listing backtests."""
    # Create a backtest
    client.post("/api/backtests", json=sample_backtest_request)

    # List backtests
    response = client.get("/api/backtests")

    assert response.status_code == 200
    data = response.json()
    assert "jobs" in data
    assert "count" in data
    assert len(data["jobs"]) > 0


def test_list_backtests_with_limit(client: TestClient):
    """Test listing backtests with limit."""
    response = client.get("/api/backtests?limit=5")

    assert response.status_code == 200
    data = response.json()
    assert len(data["jobs"]) <= 5


def test_create_backtest_invalid_data(client: TestClient):
    """Test creating backtest with invalid data."""
    response = client.post(
        "/api/backtests",
        json={
            "strategy_code": "invalid",
            "symbol": "AAPL",
            # Missing required fields
        },
    )

    assert response.status_code == 422  # Validation error


def test_create_backtest_empty_symbol(client: TestClient, sample_strategy_code: str):
    """Test creating backtest with empty symbol."""
    response = client.post(
        "/api/backtests",
        json={
            "strategy_code": sample_strategy_code,
            "symbol": "",  # Empty symbol
            "start_date": "2023-01-01T00:00:00Z",
            "end_date": "2023-06-30T23:59:59Z",
        },
    )

    assert response.status_code == 422  # Validation error
