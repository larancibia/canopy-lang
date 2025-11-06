"""
Test configuration and fixtures for API tests.
"""

import pytest
from fastapi.testclient import TestClient
from canopy.api.main import app


@pytest.fixture
def client():
    """
    Test client fixture.

    Returns:
        TestClient instance for making API requests
    """
    return TestClient(app)


@pytest.fixture
def sample_strategy_code():
    """
    Sample Canopy strategy code for testing.

    Returns:
        Valid strategy code string
    """
    return '''strategy "MA Crossover"

fast_ma = sma(close, 50)
slow_ma = sma(close, 200)

buy when crossover(fast_ma, slow_ma)
sell when crossunder(fast_ma, slow_ma)

plot(fast_ma, "Fast MA (50)", color=blue)
plot(slow_ma, "Slow MA (200)", color=red)
'''


@pytest.fixture
def invalid_strategy_code():
    """
    Invalid Canopy strategy code for testing.

    Returns:
        Invalid strategy code string
    """
    return '''fast_ma = sma(close, 50)
slow_ma = sma(close, 200)

buy when crossover(fast_ma, slow_ma)
'''  # Missing strategy name


@pytest.fixture
def sample_backtest_request(sample_strategy_code):
    """
    Sample backtest request payload.

    Returns:
        Dictionary with backtest request data
    """
    return {
        "strategy_code": sample_strategy_code,
        "symbol": "AAPL",
        "start_date": "2023-01-01T00:00:00Z",
        "end_date": "2023-06-30T23:59:59Z",
        "initial_capital": 10000.0,
        "commission": 0.001,
        "slippage": 0.0,
        "data_provider": "yahoo",
    }
