# Canopy - Modern Trading Language

[![Tests](https://github.com/canopy-lang/canopy/workflows/tests/badge.svg)](https://github.com/canopy-lang/canopy/actions)
[![codecov](https://codecov.io/gh/canopy-lang/canopy/branch/main/graph/badge.svg)](https://codecov.io/gh/canopy-lang/canopy)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A modern, intuitive trading strategy language that makes algorithmic trading accessible to everyone.

## Quick Start

```canopy
strategy "MA Crossover"

fast_ma = sma(close, 50)
slow_ma = sma(close, 200)

buy when crossover(fast_ma, slow_ma)
sell when crossunder(fast_ma, slow_ma)

plot(fast_ma, "Fast MA", color=blue)
plot(slow_ma, "Slow MA", color=red)
```

## Features

- **Intuitive Syntax**: Natural language-like syntax that traders understand
- **Backtesting Engine**: Test strategies against historical data
- **Multiple Data Sources**: Support for Yahoo Finance, CSV, and more
- **Hexagonal Architecture**: Clean, maintainable, and extensible codebase
- **Type Safety**: Built with Pydantic for robust data validation
- **TDD Approach**: Comprehensive test coverage from day one
- **CLI Interface**: Easy-to-use command-line tools
- **Free & Open Source**: MIT licensed

## Installation

### Prerequisites

- Python 3.11 or higher
- Poetry (for dependency management)

### Install with Poetry

```bash
# Clone the repository
git clone https://github.com/canopy-lang/canopy.git
cd canopy

# Install dependencies
make install

# Activate virtual environment
poetry shell
```

### Quick Test

```bash
# Run tests
make test

# Run tests with coverage
make test-cov

# Run tests in watch mode (TDD)
make test-watch
```

## Usage

### Running a Strategy

```bash
canopy run examples/ma_crossover.canopy --data SPY --start 2020-01-01 --end 2023-12-31
```

### Backtesting

```bash
canopy backtest examples/ma_crossover.canopy --data SPY --initial-capital 10000
```

### Interactive Mode

```bash
canopy repl
```

## Architecture

Canopy follows **Hexagonal Architecture** (Ports & Adapters) for clean separation of concerns:

```
┌─────────────────────────────────────────────────────┐
│                   Application                        │
│              (Use Cases & Workflows)                 │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────┴──────────────────────────────────┐
│                    Domain                            │
│         (Core Business Logic - Strategy,             │
│          Indicators, Orders, Positions)              │
└──────────────────┬──────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
   ┌────▼────┐           ┌────▼────┐
   │  Ports  │           │  Ports  │
   │  (In)   │           │  (Out)  │
   └────┬────┘           └────┬────┘
        │                     │
   ┌────▼──────────────────────▼────┐
   │         Adapters                │
   │  • Data (CSV, Yahoo Finance)    │
   │  • Engines (Backtester)         │
   │  • UI (CLI, Web)                │
   └─────────────────────────────────┘
```

### Project Structure

```
canopy/
├── src/canopy/           # Source code
│   ├── domain/           # Core business logic
│   ├── ports/            # Interface definitions
│   ├── adapters/         # External integrations
│   ├── application/      # Use cases
│   └── parser/           # Language parser
├── tests/                # Test suite
│   ├── unit/            # Unit tests
│   ├── integration/     # Integration tests
│   └── fixtures/        # Test data
└── examples/            # Example strategies
```

## Development

### Development Workflow

We follow **Test-Driven Development (TDD)**:

1. Write a failing test
2. Write minimal code to pass the test
3. Refactor
4. Repeat

```bash
# Run tests in watch mode
make test-watch
```

### Code Quality

```bash
# Format code
make format

# Run linters
make lint

# Run all checks
make all
```

### Available Make Commands

| Command | Description |
|---------|-------------|
| `make install` | Install dependencies with Poetry |
| `make test` | Run all tests with pytest |
| `make test-watch` | Run tests in watch mode (TDD) |
| `make test-cov` | Run tests with coverage report |
| `make format` | Format code with black and isort |
| `make lint` | Run linters (flake8 + mypy) |
| `make clean` | Remove build artifacts and cache |
| `make all` | Run format, lint, and test |

## Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Write tests first** (TDD approach)
4. **Implement your feature**
5. **Ensure tests pass**: `make test`
6. **Format code**: `make format`
7. **Run linters**: `make lint`
8. **Commit changes**: `git commit -m 'Add amazing feature'`
9. **Push to branch**: `git push origin feature/amazing-feature`
10. **Open a Pull Request**

### Contribution Guidelines

- Follow TDD: Write tests before implementation
- Maintain test coverage above 80%
- Follow the existing code style (black + isort)
- Update documentation for new features
- Keep commits atomic and well-described
- Respect the hexagonal architecture

## Roadmap

### Phase 1: MVP (Current)
- [x] Project setup
- [ ] Core domain models
- [ ] Language parser
- [ ] Basic backtesting engine
- [ ] CSV data adapter
- [ ] CLI interface

### Phase 2: Alpha
- [ ] Yahoo Finance adapter
- [ ] Advanced indicators
- [ ] Position sizing
- [ ] Risk management
- [ ] Performance metrics
- [ ] Web UI

### Phase 3: Beta
- [ ] Real-time data
- [ ] Paper trading
- [ ] Multiple brokers
- [ ] Cloud deployment
- [ ] Community features

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [docs.canopy-lang.com](https://docs.canopy-lang.com)
- **Discord**: [Join our community](https://discord.gg/canopy)
- **Issues**: [GitHub Issues](https://github.com/canopy-lang/canopy/issues)
- **Email**: support@canopy-lang.com

## Acknowledgments

- Inspired by TradingView's Pine Script
- Built with Python and modern software engineering practices
- Thanks to all contributors and the open-source community

---

**Built with ❤️ by the Canopy Team**
