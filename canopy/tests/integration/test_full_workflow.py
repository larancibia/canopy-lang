"""
Full workflow integration tests.

Tests the complete end-to-end workflow from parsing to backtest results.
"""

import pytest
from canopy.parser.parser import parse_strategy
from canopy.adapters.data.csv_provider import CSVDataProvider
from canopy.adapters.engines.simple_engine import SimpleBacktestEngine
from canopy.application.run_backtest import RunBacktestUseCase
from canopy.domain.timeseries import TimeSeries
import pandas as pd
import tempfile
import os
from pathlib import Path


@pytest.fixture
def sample_strategy_code():
    """Sample strategy code for testing."""
    return """
strategy "MA Crossover Test"

fast_ma = sma(close, 10)
slow_ma = sma(close, 20)

buy when crossover(fast_ma, slow_ma)
sell when crossunder(fast_ma, slow_ma)

plot(fast_ma, "Fast MA", color=blue)
plot(slow_ma, "Slow MA", color=red)
"""


@pytest.fixture
def sample_csv_data():
    """Create sample CSV data for testing."""
    # Create sample OHLCV data in CSVDataProvider format
    dates = pd.date_range("2023-01-01", periods=100, freq="D")
    df = pd.DataFrame({
        "Date": dates,
        "Open": 100 + pd.Series(range(100)) + pd.Series(range(100)).apply(lambda x: x % 10),
        "High": 102 + pd.Series(range(100)) + pd.Series(range(100)).apply(lambda x: x % 10),
        "Low": 98 + pd.Series(range(100)) + pd.Series(range(100)).apply(lambda x: x % 10),
        "Close": 100 + pd.Series(range(100)),
        "Volume": 1000000
    })

    # Create temporary directory and CSV file
    temp_dir = tempfile.mkdtemp()
    csv_path = os.path.join(temp_dir, "TEST.csv")
    df.to_csv(csv_path, index=False)

    yield temp_dir

    # Cleanup
    os.unlink(csv_path)
    os.rmdir(temp_dir)


def test_full_workflow_with_csv(sample_strategy_code, sample_csv_data):
    """
    Test complete workflow: parse strategy, load data, run backtest, get results.
    """
    # 1. Parse strategy
    strategy = parse_strategy(sample_strategy_code)

    assert strategy is not None
    assert strategy.name == "MA Crossover Test"

    # 2. Load data
    provider = CSVDataProvider(Path(sample_csv_data))
    data = provider.get_ohlcv("TEST", "2023-01-01", "2023-12-31")

    assert data is not None
    assert len(data.close) > 0

    # 3. Run backtest
    engine = SimpleBacktestEngine()
    use_case = RunBacktestUseCase(engine, provider)

    backtest, metrics = use_case.execute_with_symbol(
        strategy=strategy,
        symbol="TEST",
        start_date="2023-01-01",
        end_date="2023-12-31",
        initial_capital=10000.0
    )

    # 4. Verify results
    assert backtest is not None
    assert metrics is not None
    assert hasattr(metrics, 'total_return')
    assert hasattr(metrics, 'sharpe_ratio')
    assert len(backtest.trades) >= 0
    assert len(backtest.equity_curve) > 0


def test_multiple_strategies_workflow(sample_csv_data):
    """
    Test running multiple strategies on the same data.
    """
    strategies = [
        """
strategy "Strategy 1"
ma20 = sma(close, 20)
buy when close > ma20
sell when close < ma20
""",
        """
strategy "Strategy 2"
rsi_ind = rsi(close, 14)
buy when rsi_ind < 30
sell when rsi_ind > 70
"""
    ]

    provider = CSVDataProvider(Path(sample_csv_data))
    engine = SimpleBacktestEngine()
    use_case = RunBacktestUseCase(engine, provider)

    results = []
    for strategy_code in strategies:
        strategy = parse_strategy(strategy_code)
        backtest, metrics = use_case.execute_with_symbol(
            strategy=strategy,
            symbol="TEST",
            start_date="2023-01-01",
            end_date="2023-12-31"
        )
        results.append((backtest, metrics))

    assert len(results) == 2
    for backtest, metrics in results:
        assert backtest is not None
        assert metrics is not None


def test_workflow_with_invalid_strategy():
    """
    Test workflow with invalid strategy code.
    """
    invalid_code = """
strategy "Invalid"
buy when invalid_function()
"""

    with pytest.raises(Exception):
        parse_strategy(invalid_code)


def test_workflow_with_missing_data(sample_strategy_code):
    """
    Test workflow with missing data file.
    """
    strategy = parse_strategy(sample_strategy_code)

    # Try to use non-existent CSV file
    with pytest.raises(Exception):
        provider = CSVDataProvider(Path("/nonexistent/directory"))
        provider.get_ohlcv("TEST", "2023-01-01", "2023-12-31")
