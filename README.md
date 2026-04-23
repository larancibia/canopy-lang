# Canopy - Modern Trading Language

Canopy is a domain-specific language (DSL) for developing and backtesting trading strategies. It provides an intuitive, Python-like syntax that makes it easy to express trading logic while maintaining the power and flexibility needed for sophisticated strategies.

## Quickstart (alpha, bring your own data)

> Alpha release — data provider adapters (Yahoo, CSV) are not yet implemented. Bring your own `pandas.DataFrame` of OHLC data.

```python
from canopy.domain.timeseries import TimeSeries
from canopy.domain.strategy import MACrossoverStrategy
from canopy.adapters.engines.simple_engine import SimpleBacktestEngine
from canopy.application.run_backtest import RunBacktestUseCase
import pandas as pd
import numpy as np

# Synthetic OHLC via random walk
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

strategy = MACrossoverStrategy(name="SMA 10/30", fast_period=10, slow_period=30)
engine = SimpleBacktestEngine()
use_case = RunBacktestUseCase(engine)
backtest, metrics = use_case.execute(
    strategy, ts,
    initial_capital=10_000.0,
    commission=0.001,
    slippage=0.0,
)

print(f"Total Return:   {metrics.total_return:.2f}%")
print(f"Sharpe Ratio:   {metrics.sharpe_ratio:.2f}")
print(f"Max Drawdown:   {metrics.max_drawdown:.2f}%")
print(f"Total Trades:   {metrics.total_trades}")
print(f"Win Rate:       {metrics.win_rate:.2f}%")
```

Expected output (approximate):

```
Total Return:   -4.70%
Sharpe Ratio:   -0.01
Max Drawdown:   -16.22%
Total Trades:   5
Win Rate:       40.00%
```

A runnable copy lives at [`canopy/examples/quickstart_byod.py`](canopy/examples/quickstart_byod.py).

> **Note:** The CLI commands like `canopy backtest --symbol AAPL` shown elsewhere in this README will be available when data provider adapters ship (tracked in issues). For now, the programmatic API above is the recommended path.

## Features

- **Intuitive Syntax**: Express trading strategies in a clear, readable format
- **Built-in Indicators**: SMA, EMA, RSI, and more technical indicators
- **Backtesting Engine**: Test your strategies against historical data
- **Rich CLI**: Beautiful command-line interface powered by Rich and Typer
- **Data Sources**: Support for Yahoo Finance and CSV data
- **Performance Metrics**: Comprehensive metrics including Sharpe ratio, Sortino ratio, drawdown, and more

## Installation

```bash
# Clone the repository
git clone https://github.com/canopy-lang/canopy.git
cd canopy/canopy

# Install with poetry
poetry install

# Or install with pip (once published)
pip install canopy-lang
```

## Quick Start

### 1. Create a New Strategy

```bash
canopy new my_strategy
```

This creates a new strategy directory with a template `strategy.canopy` file.

### 2. Edit Your Strategy

Edit `my_strategy/strategy.canopy`:

```
strategy "My MA Crossover"

# Define indicators
fast_ma = sma(close, 50)
slow_ma = sma(close, 200)

# Entry/exit rules
buy when crossover(fast_ma, slow_ma)
sell when crossunder(fast_ma, slow_ma)

# Visualization
plot(fast_ma, "Fast MA", color=blue)
plot(slow_ma, "Slow MA", color=red)
```

### 3. Run a Backtest

```bash
canopy backtest my_strategy/strategy.canopy --symbol SPY --start 2020-01-01 --end 2024-01-01
```

### 4. View Results

```
✅ Backtest Complete: My MA Crossover

┏━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Metric        ┃ Value   ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ Total Return  │ 45.23%  │
│ Sharpe Ratio  │ 1.35    │
│ Sortino Ratio │ 1.82    │
│ Max Drawdown  │ -12.34% │
│ Win Rate      │ 58.33%  │
│ Profit Factor │ 1.89    │
│ Total Trades  │ 24      │
│ Winning Trades│ 14      │
│ Losing Trades │ 10      │
┗━━━━━━━━━━━━━━━┻━━━━━━━━━┛
```

## CLI Commands

### `canopy version`

Show the Canopy version.

```bash
canopy version
```

### `canopy new`

Create a new trading strategy.

```bash
canopy new STRATEGY_NAME [--directory DIR]
```

**Arguments:**
- `STRATEGY_NAME`: Name of the strategy to create

**Options:**
- `--directory DIR`: Directory to create strategy in (default: current directory)

**Example:**
```bash
canopy new golden_cross --directory ~/strategies
```

### `canopy backtest`

Run a backtest on a strategy.

```bash
canopy backtest STRATEGY_FILE [OPTIONS]
```

**Arguments:**
- `STRATEGY_FILE`: Path to the .canopy strategy file

**Options:**
- `--symbol TEXT`: Ticker symbol (default: SPY)
- `--start TEXT`: Start date in YYYY-MM-DD format (default: 2020-01-01)
- `--end TEXT`: End date in YYYY-MM-DD format (default: 2024-12-31)
- `--capital FLOAT`: Initial capital (default: 10000.0)
- `--provider TEXT`: Data provider - "yahoo" or "csv" (default: yahoo)

**Examples:**
```bash
# Basic backtest
canopy backtest examples/ma_crossover.canopy

# Custom parameters
canopy backtest my_strategy.canopy --symbol AAPL --start 2022-01-01 --end 2023-12-31 --capital 50000
```

## Canopy Language Syntax

### Strategy Declaration

Every strategy must start with a name declaration:

```
strategy "Strategy Name"
```

### Indicators

Define technical indicators using built-in functions:

```
# Simple Moving Average
fast_sma = sma(close, 50)
slow_sma = sma(close, 200)

# Exponential Moving Average
fast_ema = ema(close, 12)
slow_ema = ema(close, 26)

# Relative Strength Index
rsi_14 = rsi(close, 14)
```

### Entry/Exit Rules

Define when to buy and sell:

```
# Buy signal
buy when crossover(fast_ma, slow_ma)

# Sell signal
sell when crossunder(fast_ma, slow_ma)
```

### Plotting (Coming Soon)

Visualize indicators on charts:

```
plot(fast_ma, "Fast MA", color=blue)
plot(slow_ma, "Slow MA", color=red)
```

### Comments

Use `#` for comments:

```
# This is a comment
fast_ma = sma(close, 50)  # Inline comment
```

## Supported Indicators

- **SMA**: Simple Moving Average - `sma(source, period)`
- **EMA**: Exponential Moving Average - `ema(source, period)`
- **RSI**: Relative Strength Index - `rsi(source, period)`

More indicators coming soon!

## Architecture

Canopy follows hexagonal (ports and adapters) architecture:

```
canopy/
├── domain/          # Core business logic
│   ├── strategy.py
│   ├── indicator.py
│   ├── signal.py
│   └── backtest.py
├── ports/           # Interfaces
│   ├── data_provider.py
│   └── backtest_engine.py
├── adapters/        # Implementations
│   ├── data/
│   ├── engines/
│   └── ui/
├── application/     # Use cases
└── parser/          # Language parser
```

## Development

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src/canopy

# Run specific test file
poetry run pytest tests/unit/test_parser/test_parser.py
```

### Parser Tests

The parser has comprehensive test coverage:

```bash
poetry run pytest tests/unit/test_parser/ -v
```

## Examples

Check the `examples/` directory for sample strategies:

- `ma_crossover.canopy`: Simple moving average crossover strategy

## Roadmap

### MVP (Current)
- ✅ Basic parser for Canopy syntax
- ✅ CLI with `new`, `version`, and `backtest` commands
- ✅ SMA, EMA, RSI indicators
- ✅ Simple backtest engine
- ✅ Yahoo Finance data provider
- ✅ Performance metrics

### Next Steps
- [ ] More technical indicators (MACD, Bollinger Bands, etc.)
- [ ] Position sizing and risk management
- [ ] Multiple data sources (Alpaca, Interactive Brokers)
- [ ] Strategy optimization
- [ ] Web-based visualization
- [ ] Live trading integration
- [ ] Portfolio backtesting

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests.

## License

MIT License - see LICENSE file for details.

## Support

- Documentation: [docs.canopy-lang.io](https://docs.canopy-lang.io)
- Issues: [GitHub Issues](https://github.com/canopy-lang/canopy/issues)
- Discussions: [GitHub Discussions](https://github.com/canopy-lang/canopy/discussions)
