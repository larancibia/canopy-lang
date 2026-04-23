"""
Canopy quickstart — Bring Your Own Data (BYOD).

Runs a full backtest using a synthetic OHLC DataFrame (random walk).
No data provider adapter required — this is the supported path while the
Yahoo / CSV adapters are still stubbed.

Setup:
    pip install canopy-lang

Run:
    python quickstart_byod.py

Data providers (Yahoo, CSV) are tracked at:
    https://github.com/larancibia/canopy-lang/issues
"""

import numpy as np
import pandas as pd

from canopy.adapters.engines.simple_engine import SimpleBacktestEngine
from canopy.application.run_backtest import RunBacktestUseCase
from canopy.domain.strategy import MACrossoverStrategy
from canopy.domain.timeseries import TimeSeries


def main() -> None:
    # Build a synthetic OHLC series via a seeded random walk (252 trading days).
    dates = pd.date_range("2024-01-01", periods=252, freq="D")
    np.random.seed(42)
    close = 100 + np.cumsum(np.random.randn(252) * 2)

    ts = TimeSeries(
        open=pd.Series(close - 0.5, index=dates),
        high=pd.Series(close + 1, index=dates),
        low=pd.Series(close - 1, index=dates),
        close=pd.Series(close, index=dates),
        volume=pd.Series([1_000_000] * 252, index=dates),
    )

    # Classic SMA 10/30 crossover.
    strategy = MACrossoverStrategy(name="SMA 10/30", fast_period=10, slow_period=30)

    engine = SimpleBacktestEngine()
    use_case = RunBacktestUseCase(engine)
    _backtest, metrics = use_case.execute(
        strategy,
        ts,
        initial_capital=10_000.0,
        commission=0.001,
        slippage=0.0,
    )

    print("Canopy BYOD quickstart — results")
    print("-" * 40)
    print(f"Total Return:   {metrics.total_return:.2f}%")
    print(f"Sharpe Ratio:   {metrics.sharpe_ratio:.2f}")
    print(f"Max Drawdown:   {metrics.max_drawdown:.2f}%")
    print(f"Total Trades:   {metrics.total_trades}")
    print(f"Win Rate:       {metrics.win_rate:.2f}%")


if __name__ == "__main__":
    main()
