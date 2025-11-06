# Canopy MVP - TDD + Arquitectura Hexagonal
## Construyendo sin Capital, Part-Time, con Calidad

**Contexto:**
- 💰 Sin capital → Todo gratis/open-source
- ⏰ Part-time → 10-15 horas/semana
- 👨‍💻 Pair programming (tú + Claude)
- ✅ TDD → Tests primero, código después
- 🏗️ Hexagonal → Ports & Adapters pattern

**Timeline realista:** 8-12 semanas para MVP funcional

---

## 🏗️ Arquitectura Hexagonal para Canopy

### Diagrama de Capas:

```
┌─────────────────────────────────────────────────────────┐
│                    ADAPTERS (UI)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ CLI      │  │ Web IDE  │  │ REST API │             │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘             │
└───────┼─────────────┼─────────────┼────────────────────┘
        │             │             │
        └─────────────┼─────────────┘
                      │
┌─────────────────────▼─────────────────────────────────┐
│                    PORTS                               │
│  ┌─────────────────────────────────────────────────┐  │
│  │  IStrategyRunner                                │  │
│  │  IDataProvider                                  │  │
│  │  IBacktestEngine                                │  │
│  │  IIndicatorLibrary                              │  │
│  └─────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
                      │
┌─────────────────────▼─────────────────────────────────┐
│              DOMAIN (Core Logic)                       │
│  ┌──────────────┐  ┌──────────────┐                   │
│  │ Strategy     │  │ Backtest     │                   │
│  │ - signals    │  │ - equity     │                   │
│  │ - indicators │  │ - metrics    │                   │
│  │ - rules      │  │ - trades     │                   │
│  └──────────────┘  └──────────────┘                   │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐                   │
│  │ Indicator    │  │ TimeSeries   │                   │
│  │ - calculate  │  │ - ohlcv      │                   │
│  │ - validate   │  │ - operators  │                   │
│  └──────────────┘  └──────────────┘                   │
└────────────────────────────────────────────────────────┘
                      │
┌─────────────────────▼─────────────────────────────────┐
│              ADAPTERS (Infrastructure)                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │ CSV Data │  │ Alpaca   │  │ Yahoo    │           │
│  │ Adapter  │  │ Adapter  │  │ Adapter  │           │
│  └──────────┘  └──────────┘  └──────────┘           │
│                                                        │
│  ┌──────────┐  ┌──────────┐                          │
│  │ Vectorbt │  │ Custom   │                          │
│  │ Engine   │  │ Engine   │                          │
│  └──────────┘  └──────────┘                          │
└────────────────────────────────────────────────────────┘
```

---

## 📁 Estructura del Proyecto

```
canopy/
├── README.md
├── pyproject.toml          # Poetry para dependencies
├── Makefile                # Comandos comunes
├── .github/
│   └── workflows/
│       └── tests.yml       # CI con GitHub Actions (gratis)
│
├── src/
│   └── canopy/
│       ├── __init__.py
│       │
│       ├── domain/         # ⬡ CORE - Sin dependencies externas
│       │   ├── __init__.py
│       │   ├── strategy.py
│       │   ├── backtest.py
│       │   ├── indicator.py
│       │   ├── timeseries.py
│       │   ├── signal.py
│       │   └── portfolio.py
│       │
│       ├── ports/          # ⬡ INTERFACES
│       │   ├── __init__.py
│       │   ├── data_provider.py      # Interface
│       │   ├── backtest_engine.py    # Interface
│       │   ├── strategy_runner.py    # Interface
│       │   └── indicator_library.py  # Interface
│       │
│       ├── adapters/       # ⬡ IMPLEMENTATIONS
│       │   ├── __init__.py
│       │   │
│       │   ├── data/       # Data adapters
│       │   │   ├── __init__.py
│       │   │   ├── csv_provider.py
│       │   │   ├── alpaca_provider.py
│       │   │   └── yahoo_provider.py
│       │   │
│       │   ├── engines/    # Backtest engines
│       │   │   ├── __init__.py
│       │   │   ├── vectorbt_engine.py
│       │   │   └── simple_engine.py
│       │   │
│       │   └── ui/         # UI adapters
│       │       ├── __init__.py
│       │       ├── cli.py
│       │       └── api.py  # FastAPI REST API
│       │
│       ├── application/    # ⬡ USE CASES
│       │   ├── __init__.py
│       │   ├── run_backtest.py
│       │   ├── create_strategy.py
│       │   └── calculate_metrics.py
│       │
│       └── parser/         # ⬡ LANGUAGE PARSER
│           ├── __init__.py
│           ├── lexer.py
│           ├── parser.py
│           └── ast.py
│
├── tests/
│   ├── __init__.py
│   ├── unit/               # Tests unitarios (rápidos)
│   │   ├── test_domain/
│   │   │   ├── test_strategy.py
│   │   │   ├── test_backtest.py
│   │   │   ├── test_indicator.py
│   │   │   └── test_timeseries.py
│   │   │
│   │   ├── test_parser/
│   │   │   ├── test_lexer.py
│   │   │   └── test_parser.py
│   │   │
│   │   └── test_application/
│   │       └── test_run_backtest.py
│   │
│   ├── integration/        # Tests de integración
│   │   ├── test_csv_provider.py
│   │   ├── test_vectorbt_engine.py
│   │   └── test_cli.py
│   │
│   └── fixtures/           # Data de test
│       ├── sample_ohlcv.csv
│       └── sample_strategy.canopy
│
└── examples/               # Ejemplos de estrategias
    ├── ma_crossover.canopy
    ├── rsi_mean_reversion.canopy
    └── bollinger_bands.canopy
```

---

## 🛠️ Stack Tecnológico (Todo Gratis)

### Core:
```toml
[tool.poetry.dependencies]
python = "^3.11"
pydantic = "^2.0"      # Validación + type safety
pandas = "^2.0"        # Time-series data
numpy = "^1.24"        # Numerical computing
```

### Testing:
```toml
[tool.poetry.dev-dependencies]
pytest = "^7.4"        # Test framework
pytest-cov = "^4.1"    # Coverage
pytest-watch = "^4.2"  # Auto-run tests (TDD)
hypothesis = "^6.88"   # Property-based testing
```

### Backtesting:
```toml
vectorbt = "^0.26"     # Vectorized backtesting
ta-lib = "^0.4"        # Technical indicators (opcional)
```

### CLI:
```toml
typer = "^0.9"         # CLI framework
rich = "^13.5"         # Beautiful terminal output
```

### Parser (si vamos custom):
```toml
lark = "^1.1"          # Parser generator (más fácil que PLY)
# O simplemente AST manual
```

### Hosting (todo gratis):
- **Code:** GitHub (gratis, unlimited repos)
- **CI/CD:** GitHub Actions (2,000 min/mes gratis)
- **Data:** Yahoo Finance API (gratis, 15-min delay ok para MVP)
- **Backend:** Railway (gratis tier) o Vercel (gratis)
- **Frontend:** Vercel (gratis, unlimited)

---

## 🔴 TDD Workflow

### Red → Green → Refactor

**Ejemplo: Implementar indicador SMA**

### Step 1: RED (Write failing test)

```python
# tests/unit/test_domain/test_indicator.py
import pytest
import pandas as pd
from canopy.domain.indicator import SMA
from canopy.domain.timeseries import TimeSeries

def test_sma_calculates_correct_values():
    """SMA should calculate rolling mean correctly"""
    # Arrange
    prices = pd.Series([10, 20, 30, 40, 50])
    ts = TimeSeries(close=prices)

    # Act
    sma = SMA(period=3)
    result = sma.calculate(ts)

    # Assert
    expected = pd.Series([None, None, 20.0, 30.0, 40.0])
    pd.testing.assert_series_equal(result, expected)

def test_sma_validates_period():
    """SMA should reject invalid periods"""
    # Act & Assert
    with pytest.raises(ValueError, match="Period must be positive"):
        SMA(period=0)

def test_sma_handles_insufficient_data():
    """SMA should return NaN when not enough data"""
    # Arrange
    prices = pd.Series([10, 20])
    ts = TimeSeries(close=prices)

    # Act
    sma = SMA(period=5)
    result = sma.calculate(ts)

    # Assert
    assert result.isna().all()
```

**Run test (will FAIL):**
```bash
$ pytest tests/unit/test_domain/test_indicator.py -v
# FAILED - Module 'canopy.domain.indicator' not found
```

---

### Step 2: GREEN (Minimum code to pass)

```python
# src/canopy/domain/indicator.py
from abc import ABC, abstractmethod
import pandas as pd
from pydantic import BaseModel, validator

class Indicator(ABC):
    """Base class for all indicators"""

    @abstractmethod
    def calculate(self, timeseries: 'TimeSeries') -> pd.Series:
        """Calculate indicator values"""
        pass

class SMA(BaseModel):
    """Simple Moving Average indicator"""
    period: int

    @validator('period')
    def validate_period(cls, v):
        if v <= 0:
            raise ValueError("Period must be positive")
        return v

    def calculate(self, timeseries: 'TimeSeries') -> pd.Series:
        """Calculate SMA"""
        return timeseries.close.rolling(window=self.period).mean()
```

```python
# src/canopy/domain/timeseries.py
from pydantic import BaseModel
import pandas as pd

class TimeSeries(BaseModel):
    """Time-series data container"""
    close: pd.Series
    open: pd.Series = None
    high: pd.Series = None
    low: pd.Series = None
    volume: pd.Series = None

    class Config:
        arbitrary_types_allowed = True  # Allow pandas types
```

**Run test (should PASS):**
```bash
$ pytest tests/unit/test_domain/test_indicator.py -v
# ✅ test_sma_calculates_correct_values PASSED
# ✅ test_sma_validates_period PASSED
# ✅ test_sma_handles_insufficient_data PASSED
```

---

### Step 3: REFACTOR (Improve without breaking tests)

```python
# src/canopy/domain/indicator.py
from typing import Protocol
import pandas as pd

class TimeSeries(Protocol):
    """Protocol for time-series data"""
    close: pd.Series

class Indicator(ABC):
    """Base class for all indicators"""

    @abstractmethod
    def calculate(self, timeseries: TimeSeries) -> pd.Series:
        pass

    def __call__(self, timeseries: TimeSeries) -> pd.Series:
        """Allow indicator() syntax"""
        return self.calculate(timeseries)

class SMA(BaseModel):
    period: int

    @validator('period')
    def validate_period(cls, v):
        if v <= 0:
            raise ValueError("Period must be positive")
        return v

    def calculate(self, timeseries: TimeSeries) -> pd.Series:
        if len(timeseries.close) < self.period:
            return pd.Series([pd.NA] * len(timeseries.close))
        return timeseries.close.rolling(window=self.period).mean()
```

**Run tests again:**
```bash
$ pytest tests/unit/test_domain/test_indicator.py -v
# ✅ All tests still pass
```

---

## 📅 Plan de Trabajo: Primeras 4 Semanas (Part-Time)

### Week 1: Domain Core + TDD Setup (10-12 horas)

**Sesión 1 (2-3 horas): Setup**
- [ ] `poetry init` - Crear proyecto
- [ ] Setup `pytest` + `pytest-watch`
- [ ] Configurar `pyproject.toml`
- [ ] Setup GitHub repo + CI

**Sesión 2 (3-4 horas): TimeSeries Domain**
- [ ] TDD: `test_timeseries.py` (write tests)
- [ ] Implement `TimeSeries` class
- [ ] Tests para OHLCV data
- [ ] Tests para operators (`[]` indexing, slicing)

**Sesión 3 (3-4 horas): Indicator Domain**
- [ ] TDD: `test_indicator.py`
- [ ] Implement `Indicator` base class
- [ ] Implement `SMA` indicator
- [ ] Implement `EMA` indicator
- [ ] Property-based tests con Hypothesis

**Sesión 4 (2-3 horas): Signal Domain**
- [ ] TDD: `test_signal.py`
- [ ] Implement `Signal` class (buy/sell/hold)
- [ ] Tests para crossover detection
- [ ] Tests para threshold detection

**Goal Week 1:** Domain model básico con 100% test coverage

---

### Week 2: Backtest Engine (10-12 horas)

**Sesión 1 (3-4 horas): Backtest Domain**
- [ ] TDD: `test_backtest.py`
- [ ] Implement `Backtest` class
- [ ] Equity curve calculation
- [ ] Trade tracking

**Sesión 2 (3-4 horas): Metrics**
- [ ] TDD: `test_metrics.py`
- [ ] Total return calculation
- [ ] Sharpe ratio
- [ ] Max drawdown
- [ ] Win rate

**Sesión 3 (3-4 horas): Simple Engine (Ports + Adapter)**
- [ ] TDD: `test_backtest_engine.py` (port interface)
- [ ] Implement `IBacktestEngine` interface
- [ ] Implement `SimpleEngine` adapter
- [ ] Integration test con real data

**Goal Week 2:** Backtest engine funcional con metrics

---

### Week 3: Data Provider + Strategy (10-12 horas)

**Sesión 1 (3-4 horas): Data Provider Port + CSV Adapter**
- [ ] TDD: `test_data_provider.py` (interface)
- [ ] Implement `IDataProvider` port
- [ ] TDD: `test_csv_provider.py`
- [ ] Implement `CSVDataProvider` adapter
- [ ] Fixtures con sample CSV data

**Sesión 2 (3-4 horas): Yahoo Finance Adapter**
- [ ] TDD: `test_yahoo_provider.py`
- [ ] Implement `YahooDataProvider` using `yfinance`
- [ ] Error handling (network failures)
- [ ] Caching for tests

**Sesión 3 (3-4 horas): Strategy Domain**
- [ ] TDD: `test_strategy.py`
- [ ] Implement `Strategy` base class
- [ ] Implement hardcoded MA Crossover strategy
- [ ] Run end-to-end backtest

**Goal Week 3:** Data providers + primera estrategia funcional

---

### Week 4: CLI + Parser Básico (10-12 horas)

**Sesión 1 (3-4 horas): CLI Adapter**
- [ ] TDD: `test_cli.py`
- [ ] Implement `canopy backtest` command
- [ ] Implement `canopy new` command
- [ ] Beautiful output con Rich

**Sesión 2 (4-5 horas): Parser Mínimo**
- [ ] TDD: `test_parser.py`
- [ ] Implement lexer básico (tokens)
- [ ] Parser para syntax simple:
  ```canopy
  strategy "MA Crossover"
  fast = sma(close, 50)
  slow = sma(close, 200)
  buy when fast > slow
  sell when fast < slow
  ```
- [ ] AST generation

**Sesión 3 (3-4 horas): Integration End-to-End**
- [ ] Parse strategy → Execute → Show results
- [ ] Integration test completo
- [ ] README con quickstart example

**Goal Week 4:** MVP funcional CLI que parsea syntax simple y ejecuta backtest

---

## 🎯 Definición de "MVP Funcional" (Semana 4)

```bash
# User can do this:
$ pip install canopy-lang  # (o pipx install)

$ canopy new my_strategy
Created: my_strategy/strategy.canopy

$ cat my_strategy/strategy.canopy
strategy "MA Crossover"

fast_ma = sma(close, 50)
slow_ma = sma(close, 200)

buy when crossover(fast_ma, slow_ma)
sell when crossunder(fast_ma, slow_ma)

$ canopy backtest my_strategy/ --symbol=SPY --start=2020-01-01

Running backtest...
━━━━━━━━━━━━━━━━━━━━━━ 100% ━━━━━━━━━━━━━━━━━━━━━━

Strategy Performance (2020-01-01 to 2024-12-31)
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Metric           ┃ Value    ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ Total Return     │ 45.2%    │
│ Sharpe Ratio     │ 1.35     │
│ Max Drawdown     │ -12.3%   │
│ Win Rate         │ 52%      │
│ Total Trades     │ 23       │
└──────────────────┴──────────┘

Equity curve saved to: my_strategy/equity.png
```

**Este es el MVP que validamos en 4 semanas.**

---

## 🧪 TDD Commands para tu Workflow

### Setup inicial (una vez):
```bash
# Create project
$ poetry new canopy-lang
$ cd canopy-lang

# Add dependencies
$ poetry add pydantic pandas numpy typer rich
$ poetry add --group dev pytest pytest-cov pytest-watch hypothesis

# Setup git
$ git init
$ echo "__pycache__/" > .gitignore
$ echo "*.pyc" >> .gitignore
$ echo ".pytest_cache/" >> .gitignore
$ git add .
$ git commit -m "Initial commit"
```

---

### Daily TDD workflow:

```bash
# Start pytest-watch (auto-run tests on file change)
$ poetry run ptw -- -v

# In another terminal: Start coding
$ code .

# Write test first (RED)
# tests/unit/test_domain/test_indicator.py
def test_sma_calculates_correctly():
    # ... test code ...
    pass

# Watch pytest fail (RED)
# ❌ ModuleNotFoundError: No module named 'canopy.domain.indicator'

# Write minimum code to pass (GREEN)
# src/canopy/domain/indicator.py
class SMA:
    # ... implementation ...
    pass

# Watch pytest pass (GREEN)
# ✅ test_sma_calculates_correctly PASSED

# Refactor
# Improve code, tests still pass

# Commit
$ git add .
$ git commit -m "Add SMA indicator with tests"
```

---

### Commands útiles:

```bash
# Run all tests
$ poetry run pytest

# Run tests with coverage
$ poetry run pytest --cov=canopy --cov-report=html

# Run only unit tests (fast)
$ poetry run pytest tests/unit/ -v

# Run only one test file
$ poetry run pytest tests/unit/test_domain/test_indicator.py -v

# Run only one test
$ poetry run pytest tests/unit/test_domain/test_indicator.py::test_sma_calculates_correctly -v

# Watch mode (auto-run on changes)
$ poetry run ptw

# Type checking (add mypy)
$ poetry run mypy src/
```

---

## 📋 Makefile para comandos comunes

```makefile
.PHONY: test test-watch test-cov install format lint

install:
	poetry install

test:
	poetry run pytest -v

test-watch:
	poetry run ptw -- -v

test-cov:
	poetry run pytest --cov=canopy --cov-report=html --cov-report=term

format:
	poetry run black src/ tests/
	poetry run isort src/ tests/

lint:
	poetry run flake8 src/ tests/
	poetry run mypy src/

run-example:
	poetry run canopy backtest examples/ma_crossover.canopy --symbol=SPY
```

**Usage:**
```bash
$ make install      # Setup dependencies
$ make test-watch   # TDD mode
$ make test-cov     # Coverage report
$ make format       # Format code
```

---

## 🏛️ Hexagonal Architecture - Reglas Estrictas

### Domain Layer (Core):
✅ **Permitido:**
- Pure Python
- Pydantic models
- Type hints
- Business logic SOLO

❌ **Prohibido:**
- `import pandas` (solo en ports/adapters)
- `import requests`
- `import fastapi`
- Cualquier framework externo
- I/O operations
- Database access

**Ejemplo:**
```python
# ✅ BIEN - Domain puro
from pydantic import BaseModel
from typing import List

class Strategy(BaseModel):
    name: str
    signals: List[Signal]

    def generate_signals(self, data: TimeSeries) -> List[Signal]:
        # Pure business logic
        pass

# ❌ MAL - Domain con dependencies
import pandas as pd  # NO!
import requests      # NO!

class Strategy:
    def fetch_data(self):  # NO! Domain no hace I/O
        response = requests.get(...)
```

---

### Ports Layer (Interfaces):
✅ **Permitido:**
- Abstract base classes
- Protocols
- Type hints
- NO implementation

```python
# src/canopy/ports/data_provider.py
from abc import ABC, abstractmethod
from canopy.domain.timeseries import TimeSeries

class IDataProvider(ABC):
    """Port for data providers"""

    @abstractmethod
    def get_ohlcv(self, symbol: str, start: str, end: str) -> TimeSeries:
        """Fetch OHLCV data for symbol"""
        pass
```

---

### Adapters Layer (Implementations):
✅ **Permitido:**
- Implementar ports
- Usar cualquier librería externa
- I/O operations
- API calls
- Database access

```python
# src/canopy/adapters/data/yahoo_provider.py
import yfinance as yf  # OK aquí!
from canopy.ports.data_provider import IDataProvider
from canopy.domain.timeseries import TimeSeries

class YahooDataProvider(IDataProvider):
    """Yahoo Finance adapter"""

    def get_ohlcv(self, symbol: str, start: str, end: str) -> TimeSeries:
        df = yf.download(symbol, start=start, end=end)
        return TimeSeries(
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            volume=df['Volume']
        )
```

---

## 🎯 Dependency Injection

**Application layer conecta todo:**

```python
# src/canopy/application/run_backtest.py
from canopy.ports.data_provider import IDataProvider
from canopy.ports.backtest_engine import IBacktestEngine
from canopy.domain.strategy import Strategy

class RunBacktestUseCase:
    """Application use case for running backtests"""

    def __init__(
        self,
        data_provider: IDataProvider,
        backtest_engine: IBacktestEngine
    ):
        self.data_provider = data_provider
        self.backtest_engine = backtest_engine

    def execute(
        self,
        strategy: Strategy,
        symbol: str,
        start: str,
        end: str
    ) -> BacktestResult:
        # 1. Fetch data (via port)
        data = self.data_provider.get_ohlcv(symbol, start, end)

        # 2. Run backtest (via port)
        result = self.backtest_engine.run(strategy, data)

        return result
```

**CLI wires everything up:**

```python
# src/canopy/adapters/ui/cli.py
import typer
from canopy.adapters.data.yahoo_provider import YahooDataProvider
from canopy.adapters.engines.simple_engine import SimpleBacktestEngine
from canopy.application.run_backtest import RunBacktestUseCase

app = typer.Typer()

@app.command()
def backtest(
    strategy_file: str,
    symbol: str = "SPY",
    start: str = "2020-01-01",
    end: str = "2024-12-31"
):
    """Run a backtest"""
    # Dependency injection
    data_provider = YahooDataProvider()
    backtest_engine = SimpleBacktestEngine()

    use_case = RunBacktestUseCase(
        data_provider=data_provider,
        backtest_engine=backtest_engine
    )

    # Parse strategy from file
    with open(strategy_file) as f:
        strategy_code = f.read()

    strategy = parse_strategy(strategy_code)

    # Execute use case
    result = use_case.execute(strategy, symbol, start, end)

    # Display results
    print_results(result)
```

**Benefits:**
- ✅ Easy to test (mock ports)
- ✅ Easy to swap adapters (Yahoo → Alpaca)
- ✅ Domain stays pure
- ✅ Flexible architecture

---

## 🚀 Próximo Paso INMEDIATO

### En las próximas 2 horas, hacemos esto juntos:

1. **Setup proyecto:**
```bash
$ poetry new canopy-lang
$ cd canopy-lang
$ poetry add pydantic pandas numpy
$ poetry add --group dev pytest pytest-watch
```

2. **Primer test (TDD):**
```python
# tests/unit/test_domain/test_timeseries.py
def test_timeseries_stores_ohlcv_data():
    """TimeSeries should store OHLCV data"""
    # Write this test first (will fail)
    pass
```

3. **Implement:**
```python
# src/canopy/domain/timeseries.py
class TimeSeries:
    # Make test pass
    pass
```

4. **Commit:**
```bash
$ git init
$ git add .
$ git commit -m "Add TimeSeries with test"
```

---

## ✅ ¿Estás listo para empezar?

**Dime:**
1. ¿Tienes Python 3.11+ instalado?
2. ¿Tienes Poetry instalado? (si no: `pip install poetry`)
3. ¿Qué editor usas? (VS Code recomendado)
4. ¿En qué sistema? (Mac/Linux/Windows)

**Una vez confirmes, empezamos con el setup y el primer test TDD en esta misma sesión.** 🚀
