# 🌳 Canopy Trading Language

A powerful, expressive domain-specific language (DSL) for trading strategy development and backtesting.

> ⚠️  **Alpha release (v0.0.1)** — The core DSL, parser, backtest engine, optimizers (Bayesian/Genetic/Grid), and metrics are working (264 unit tests passing). **Data provider adapters (Yahoo Finance, CSV) are not yet implemented in this release** — bring your own `pandas.DataFrame` of OHLC data for now. The REST API and web frontend mentioned below are experimental and require `pip install canopy-lang[web]`. API may change before 1.0.



[![Tests](https://github.com/larancibia/canopy-lang/actions/workflows/tests.yml/badge.svg)](https://github.com/larancibia/canopy-lang/actions/workflows/tests.yml)
[![Docker Build](https://github.com/larancibia/canopy-lang/actions/workflows/docker-build.yml/badge.svg)](https://github.com/larancibia/canopy-lang/actions/workflows/docker-build.yml)
[![codecov](https://codecov.io/gh/larancibia/canopy-lang/branch/main/graph/badge.svg)](https://codecov.io/gh/larancibia/canopy-lang)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Quickstart (alpha, bring your own data)

The simplest way to run a backtest today — no data provider adapter needed. Bring a `pandas.DataFrame` (or the four `pd.Series` shown below) and go:

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

A runnable copy lives at [`examples/quickstart_byod.py`](examples/quickstart_byod.py).

> **Note:** The CLI commands like `canopy backtest --symbol AAPL` shown elsewhere in this README will be available when data provider adapters ship (tracked in issues). For now, the programmatic API above is the recommended path.

## ✨ Features

- **📝 Intuitive DSL**: Write trading strategies in a clear, expressive language
- **📊 Technical Indicators**: 15+ built-in indicators (SMA, EMA, RSI, MACD, Bollinger Bands, etc.)
- **🔙 Fast Backtesting**: Vectorized backtest engine for quick results
- **📈 Performance Metrics**: Comprehensive metrics (Sharpe, Sortino, drawdown, win rate, etc.)
- **🌐 REST API**: FastAPI-powered API for programmatic access
- **💻 Web Interface**: React-based frontend for visual strategy development
- **🐳 Docker Ready**: Complete Docker Compose setup for easy deployment
- **🧪 Production Ready**: Built with hexagonal architecture and TDD
- **📚 Rich Examples**: 10+ example strategies from basic to advanced

## 🚀 Quick Start

### With Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/larancibia/canopy-lang.git
cd canopy

# Start all services
docker-compose up

# Access the services
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Web UI: http://localhost:5173
```

### Local Development

```bash
# Run setup script
./scripts/setup.sh

# Start development servers
./scripts/run-dev.sh
```

### Simple Example

Create a file `my_strategy.canopy`:

```canopy
strategy "MA Crossover"

# Define moving averages
fast_ma = sma(close, 50)
slow_ma = sma(close, 200)

# Entry: Buy when fast crosses above slow
buy when crossover(fast_ma, slow_ma)

# Exit: Sell when fast crosses below slow
sell when crossunder(fast_ma, slow_ma)

# Visualize
plot(fast_ma, "Fast MA", color=blue)
plot(slow_ma, "Slow MA", color=red)
```

Run the backtest:

```bash
# CLI
canopy backtest my_strategy.canopy --symbol AAPL --start 2022-01-01 --end 2023-12-31

# Python API
from canopy import run_backtest

result = run_backtest(
    strategy_file="my_strategy.canopy",
    symbol="AAPL",
    start_date="2022-01-01",
    end_date="2023-12-31"
)

print(f"Total Return: {result.metrics.total_return:.2%}")
print(f"Sharpe Ratio: {result.metrics.sharpe_ratio:.2f}")
```

## 📚 Documentation

- **[Language Reference](docs/LANGUAGE_REFERENCE.md)** - Complete language syntax and indicators
- **[API Reference](docs/API_REFERENCE.md)** - REST API documentation
- **[Architecture](docs/ARCHITECTURE.md)** - System architecture and design
- **[Development Guide](docs/DEVELOPMENT.md)** - Contributing and development
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment

## 🎯 Example Strategies

### Basic Strategies

- **[MA Crossover](examples/strategies/basic/ma_crossover.canopy)** - Golden/Death cross
- **[RSI Mean Reversion](examples/strategies/basic/rsi_meanreversion.canopy)** - Oversold/overbought
- **[EMA Crossover](examples/strategies/basic/ema_crossover.canopy)** - Exponential MAs
- **[Volume Breakout](examples/strategies/basic/volume_breakout.canopy)** - High volume breaks

### Advanced Strategies

- **[Bollinger Squeeze](examples/strategies/advanced/bollinger_squeeze.canopy)** - Volatility breakout
- **[MACD Divergence](examples/strategies/advanced/macd_divergence.canopy)** - Momentum trading
- **[ATR Breakout](examples/strategies/advanced/atr_breakout.canopy)** - Volatility-based
- **[Multi-Timeframe](examples/strategies/advanced/multi_timeframe.canopy)** - Cross-timeframe

### Portfolio Strategies

- **[Pairs Trading](examples/strategies/portfolio/pairs_trading.canopy)** - Mean reversion pairs
- **[Sector Rotation](examples/strategies/portfolio/sector_rotation.canopy)** - Relative strength

### Python Examples

- **[Custom Indicators](examples/python/custom_indicator.py)** - Build your own indicators
- **[ML Strategy](examples/python/ml_strategy.py)** - Machine learning integration
- **[Optimization](examples/optimization/optimize_ma_crossover.py)** - Parameter optimization

## 🏗️ Architecture

Canopy is built using **Hexagonal Architecture** (Ports and Adapters):

```
┌─────────────────────────────────────────┐
│           UI Layer                      │
│   CLI  │  Web API  │  Web Frontend     │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│      Application Layer (Use Cases)      │
│   Run Backtest  │  Fetch Data  │  ...   │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│     Domain Layer (Business Logic)       │
│  Strategy │ Indicator │ Signal │ ...    │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│       Ports (Interfaces)                │
│  IDataProvider  │  IBacktestEngine      │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│     Adapters (Implementations)          │
│  Yahoo │ CSV │ Simple Engine │ ...      │
└─────────────────────────────────────────┘
```

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for details.

## 🛠️ Tech Stack

### Backend
- **Python 3.11+** - Core language
- **FastAPI** - REST API framework
- **Pandas & NumPy** - Data processing
- **Pydantic** - Data validation
- **yfinance** - Market data

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **Recharts** - Charting

### Infrastructure
- **Docker & Docker Compose** - Containerization
- **PostgreSQL** - Database
- **Redis** - Caching and job queue
- **GitHub Actions** - CI/CD

## 🧪 Testing

```bash
# Run all tests
./scripts/test-all.sh

# Run unit tests only
poetry run pytest tests/unit -v

# Run integration tests
poetry run pytest tests/integration -v

# Run with coverage
poetry run pytest --cov=src/canopy --cov-report=html
```

## 📦 Installation

### From Source

```bash
# Clone repository
git clone https://github.com/larancibia/canopy-lang.git
cd canopy

# Install with Poetry
poetry install

# Or with pip (when published)
pip install canopy-lang
```

### Docker

```bash
# Pull images
docker pull ghcr.io/larancibia/canopy-lang/api:latest
docker pull ghcr.io/larancibia/canopy-lang/web:latest

# Run with Docker Compose
docker-compose up
```

## 🤝 Contributing

We welcome contributions! Please see our [Development Guide](docs/DEVELOPMENT.md).

```bash
# Setup development environment
./scripts/setup.sh

# Create a feature branch
git checkout -b feature/amazing-feature

# Make changes and run tests
./scripts/test-all.sh

# Commit and push
git commit -m "Add amazing feature"
git push origin feature/amazing-feature
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Roadmap

### MVP (Current)
- [x] Core DSL parser
- [x] Basic indicators
- [x] Simple backtest engine
- [x] CLI interface
- [x] REST API
- [x] Web frontend
- [x] Docker deployment

### v0.2.0 (Next)
- [ ] Portfolio backtesting (multi-asset)
- [ ] Walk-forward optimization
- [ ] Real-time data feeds
- [ ] More indicators (50+)
- [ ] Custom indicator creation UI

### v0.3.0 (Future)
- [ ] Live trading integration
- [ ] Machine learning integration
- [ ] Options and futures support
- [ ] Social trading features
- [ ] Cloud hosting (SaaS)

## 📞 Support

- **Documentation**: [github.com/larancibia/canopy-lang#readme](https://github.com/larancibia/canopy-lang#readme)
- **Issues**: [GitHub Issues](https://github.com/larancibia/canopy-lang/issues)
- **Discussions**: [GitHub Discussions](https://github.com/larancibia/canopy-lang/discussions)
- **Email**: arancibialuisalejandro@gmail.com

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Inspired by [Pine Script](https://www.tradingview.com/pine-script-docs/)
- Data from [yfinance](https://github.com/ranaroussi/yfinance)

---

**Made with ❤️ by Luis Arancibia**

⭐ Star us on GitHub if you find this project helpful!
