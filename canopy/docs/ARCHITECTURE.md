# Canopy Architecture

## Overview

Canopy is built using **Hexagonal Architecture** (Ports and Adapters), which provides clean separation between business logic and external concerns. This architecture makes the system highly testable, maintainable, and extensible.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         UI Layer                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │     CLI      │  │  Web API     │  │  Web Frontend│          │
│  │   (Typer)    │  │  (FastAPI)   │  │   (React)    │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
┌────────────────────────────┼─────────────────────────────────────┐
│                    Application Layer                             │
│              (Use Cases / Business Workflows)                    │
│                                                                  │
│  ┌───────────────────┐  ┌─────────────────┐  ┌──────────────┐  │
│  │ Run Backtest      │  │ Fetch Data      │  │ Parse Strategy│  │
│  │ Use Case          │  │ Use Case        │  │ Use Case      │  │
│  └─────────┬─────────┘  └────────┬────────┘  └──────┬───────┘  │
└────────────┼────────────────────────┼─────────────────┼──────────┘
             │                       │                  │
┌────────────┼───────────────────────┼──────────────────┼──────────┐
│            │          Domain Layer (Core Business Logic)         │
│            │                                                      │
│  ┌─────────▼─────────┐  ┌─────────▼────────┐  ┌────────▼──────┐ │
│  │   Strategy        │  │  Backtest Result │  │  Indicator    │ │
│  │   (Entity)        │  │  (Value Object)  │  │  (Entity)     │ │
│  └───────────────────┘  └──────────────────┘  └───────────────┘ │
│                                                                  │
│  ┌───────────────────┐  ┌──────────────────┐  ┌───────────────┐ │
│  │   Signal          │  │  TimeSeries      │  │  Metrics      │ │
│  │   (Value Object)  │  │  (Entity)        │  │  (Calculator) │ │
│  └───────────────────┘  └──────────────────┘  └───────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────┼─────────────────────────────────────┐
│                       Ports Layer                                │
│                    (Interfaces/Contracts)                        │
│                                                                  │
│  ┌───────────────────┐            ┌──────────────────┐          │
│  │ IDataProvider     │            │ IBacktestEngine  │          │
│  │ (Port)            │            │ (Port)           │          │
│  └─────────┬─────────┘            └────────┬─────────┘          │
└────────────┼──────────────────────────────────┼─────────────────┘
             │                                  │
┌────────────┼──────────────────────────────────┼─────────────────┐
│                      Adapters Layer                              │
│              (External System Implementations)                   │
│                                                                  │
│  ┌─────────▼─────────┐            ┌────────▼──────────┐         │
│  │ Yahoo Finance     │            │ Simple Engine     │         │
│  │ Provider          │            │ (Vectorized)      │         │
│  └───────────────────┘            └───────────────────┘         │
│                                                                  │
│  ┌───────────────────┐            ┌───────────────────┐         │
│  │ CSV Provider      │            │ Event-Driven      │         │
│  │                   │            │ Engine (Future)   │         │
│  └───────────────────┘            └───────────────────┘         │
│                                                                  │
│  ┌───────────────────┐            ┌───────────────────┐         │
│  │ Alpaca Provider   │            │ Portfolio Engine  │         │
│  │ (Future)          │            │ (Multi-Asset)     │         │
│  └───────────────────┘            └───────────────────┘         │
└──────────────────────────────────────────────────────────────────┘
```

## Layer Responsibilities

### 1. Domain Layer (Core)

**Purpose**: Contains pure business logic with no external dependencies.

**Components**:
- **Entities**: Strategy, Indicator, TimeSeries, Backtest
- **Value Objects**: Signal, Bar, Trade, Metrics
- **Domain Services**: MetricsCalculator

**Rules**:
- No framework dependencies
- No I/O operations
- Pure functions where possible
- Easily testable in isolation

**Example**:
```python
# src/canopy/domain/strategy.py
class Strategy:
    def __init__(self, name: str):
        self.name = name
        self.indicators: List[Indicator] = []
        self.signals: List[Signal] = []
```

### 2. Ports Layer (Interfaces)

**Purpose**: Defines contracts for external interactions.

**Components**:
- **IDataProvider**: Interface for data sources
- **IBacktestEngine**: Interface for backtest execution

**Example**:
```python
# src/canopy/ports/data_provider.py
class IDataProvider(ABC):
    @abstractmethod
    def fetch_data(self, symbol: str, start_date: str, end_date: str) -> TimeSeries:
        pass
```

### 3. Application Layer (Use Cases)

**Purpose**: Orchestrates domain objects to fulfill business workflows.

**Components**:
- **RunBacktestUseCase**: Execute a complete backtest
- **FetchDataUseCase**: Retrieve and prepare market data
- **ParseStrategyUseCase**: Parse Canopy DSL

**Rules**:
- Depends on domain and ports (interfaces)
- No implementation details
- Transaction boundaries
- Error handling and validation

**Example**:
```python
# src/canopy/application/run_backtest.py
class RunBacktestUseCase:
    def __init__(self, data_provider: IDataProvider, engine: IBacktestEngine):
        self.data_provider = data_provider
        self.engine = engine

    def execute(self, strategy, symbol, start_date, end_date):
        # Orchestrate the backtest workflow
        data = self.data_provider.fetch_data(symbol, start_date, end_date)
        return self.engine.run(strategy, data)
```

### 4. Adapters Layer (Implementations)

**Purpose**: Implement ports for external systems.

**Components**:
- **Data Adapters**: YahooProvider, CSVProvider, AlpacaProvider
- **Engine Adapters**: SimpleEngine, PortfolioEngine
- **UI Adapters**: CLI, FastAPI routes

**Rules**:
- Implements port interfaces
- Handles external system specifics
- Converts between external and domain models

### 5. UI Layer

**Purpose**: User-facing interfaces.

**Components**:
- **CLI**: Command-line interface (Typer)
- **Web API**: REST API (FastAPI)
- **Web Frontend**: React application

## Data Flow

### Backtest Workflow

```
1. User Input (CLI/API)
   │
   ▼
2. Application Layer (RunBacktestUseCase)
   │
   ├─► Parse Strategy (Parser)
   │   │
   │   ▼
   │   Strategy Entity (Domain)
   │
   ├─► Fetch Data (IDataProvider Port)
   │   │
   │   ▼
   │   Data Adapter (Yahoo/CSV)
   │   │
   │   ▼
   │   TimeSeries Entity (Domain)
   │
   └─► Run Backtest (IBacktestEngine Port)
       │
       ▼
       Engine Adapter (Simple/Portfolio)
       │
       ▼
       BacktestResult (Domain)
       │
       ▼
3. Calculate Metrics (MetricsCalculator)
   │
   ▼
4. Return Results (JSON/CLI Output)
```

## Technology Stack

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI (Web API)
- **CLI**: Typer
- **Validation**: Pydantic
- **Data**: Pandas, NumPy
- **Testing**: Pytest

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: TailwindCSS
- **Charts**: Recharts / Plotly
- **State**: React Query / Zustand

### Infrastructure
- **Containerization**: Docker, Docker Compose
- **Database**: PostgreSQL (future)
- **Cache**: Redis
- **CI/CD**: GitHub Actions

## Design Patterns

### 1. Dependency Injection

All use cases receive dependencies through constructor injection:

```python
use_case = RunBacktestUseCase(
    data_provider=YahooProvider(),
    engine=SimpleEngine()
)
```

### 2. Strategy Pattern

Multiple implementations of the same interface:

```python
# Different data providers
yahoo_provider = YahooProvider()
csv_provider = CSVProvider()
alpaca_provider = AlpacaProvider()

# All implement IDataProvider
```

### 3. Factory Pattern

Create objects based on configuration:

```python
provider = DataProviderFactory.create("yahoo")
```

### 4. Repository Pattern (Future)

For persistence:

```python
strategy_repo = StrategyRepository()
strategy = strategy_repo.get_by_id(123)
```

## Testing Strategy

### Unit Tests
- Test domain logic in isolation
- Fast, no external dependencies
- High coverage requirement (>90%)

### Integration Tests
- Test adapter implementations
- Test use case workflows
- Test with real external services (or mocks)

### End-to-End Tests
- Test full user workflows
- CLI commands
- API endpoints

## Extending the System

### Adding a New Data Provider

1. Implement `IDataProvider` interface
2. Add to `DataProviderFactory`
3. Add configuration
4. Write tests

### Adding a New Indicator

1. Create indicator function in `domain/indicator.py`
2. Update parser to recognize it
3. Add documentation
4. Write tests

### Adding a New Backtest Engine

1. Implement `IBacktestEngine` interface
2. Add to factory or configuration
3. Write tests

## Benefits of This Architecture

1. **Testability**: Domain logic tested in isolation
2. **Flexibility**: Easy to swap implementations
3. **Maintainability**: Clear separation of concerns
4. **Scalability**: Can grow without becoming monolithic
5. **Team Collaboration**: Teams can work on different layers independently

## Directory Structure

```
canopy/
├── src/canopy/
│   ├── domain/          # Core business logic
│   ├── ports/           # Interface definitions
│   ├── application/     # Use cases
│   ├── adapters/        # External implementations
│   │   ├── data/        # Data providers
│   │   ├── engines/     # Backtest engines
│   │   └── ui/          # CLI, API
│   ├── parser/          # DSL parser
│   └── api/             # FastAPI application
├── tests/
│   ├── unit/            # Unit tests
│   └── integration/     # Integration tests
├── examples/            # Example strategies
└── docs/                # Documentation
```

## Next Steps

- [ ] Add PostgreSQL for strategy persistence
- [ ] Implement event-driven backtest engine
- [ ] Add WebSocket support for real-time updates
- [ ] Implement portfolio optimization engine
- [ ] Add ML integration capabilities
