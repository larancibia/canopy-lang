"""
Tests for strategy endpoints.
"""

import pytest
from fastapi.testclient import TestClient


def test_parse_valid_strategy(client: TestClient, sample_strategy_code: str):
    """Test parsing a valid strategy."""
    response = client.post(
        "/api/strategies/parse", json={"strategy_code": sample_strategy_code}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["strategy_name"] == "MA Crossover"
    assert data["indicators"] is not None
    assert "fast_ma" in data["indicators"]
    assert "slow_ma" in data["indicators"]


def test_parse_invalid_strategy(client: TestClient, invalid_strategy_code: str):
    """Test parsing an invalid strategy."""
    response = client.post(
        "/api/strategies/parse", json={"strategy_code": invalid_strategy_code}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["error"] is not None


def test_validate_valid_strategy(client: TestClient, sample_strategy_code: str):
    """Test validating a valid strategy."""
    response = client.post(
        "/api/strategies/validate", json={"strategy_code": sample_strategy_code}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["error"] is None


def test_validate_invalid_strategy(client: TestClient, invalid_strategy_code: str):
    """Test validating an invalid strategy."""
    response = client.post(
        "/api/strategies/validate", json={"strategy_code": invalid_strategy_code}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert data["error"] is not None


def test_list_examples(client: TestClient):
    """Test listing example strategies."""
    response = client.get("/api/strategies/examples")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(ex["name"] == "ma_crossover" for ex in data)


def test_get_example(client: TestClient):
    """Test getting a specific example strategy."""
    response = client.get("/api/strategies/examples/ma_crossover")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "ma_crossover"
    assert "code" in data
    assert "description" in data
    assert len(data["code"]) > 0


def test_get_nonexistent_example(client: TestClient):
    """Test getting a non-existent example."""
    response = client.get("/api/strategies/examples/nonexistent")

    assert response.status_code == 404
    data = response.json()
    # Error message is in either 'detail' or 'error' field
    error_msg = (data.get("detail") or data.get("error", "")).lower()
    assert "not found" in error_msg


def test_parse_missing_code(client: TestClient):
    """Test parsing with missing code."""
    response = client.post("/api/strategies/parse", json={})

    assert response.status_code == 422  # Validation error


def test_parse_empty_code(client: TestClient):
    """Test parsing with empty code."""
    response = client.post("/api/strategies/parse", json={"strategy_code": ""})

    assert response.status_code == 422  # Validation error (min_length=1)
