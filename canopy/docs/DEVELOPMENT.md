# Development Guide

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Poetry (Python package manager)
- Node.js 18+ and npm (for web frontend)
- Docker and Docker Compose (optional, for containerized development)
- Git

### Initial Setup

#### 1. Clone the Repository

```bash
git clone https://github.com/your-org/canopy-lang.git
cd canopy-lang/canopy
```

#### 2. Run Setup Script

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

This will:
- Install Poetry
- Install Python dependencies
- Setup pre-commit hooks
- Install frontend dependencies
- Create .env file from template

#### 3. Manual Setup (Alternative)

**Install Python Dependencies**:
```bash
poetry install
```

**Install Frontend Dependencies**:
```bash
cd web
npm install
cd ..
```

**Create Environment File**:
```bash
cp .env.example .env
```

### Running the Application

#### Option 1: Docker Compose (Recommended)

Start all services:
```bash
docker-compose up
```

Services will be available at:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Web Frontend: http://localhost:5173
- PostgreSQL: localhost:5432
- Redis: localhost:6379

Stop services:
```bash
docker-compose down
```

#### Option 2: Local Development

**Start API**:
```bash
poetry run uvicorn canopy.api.main:app --reload
```

**Start Web Frontend**:
```bash
cd web
npm run dev
```

**Start Redis (if needed)**:
```bash
docker run -p 6379:6379 redis:7-alpine
```

#### Option 3: Use Development Script

```bash
./scripts/run-dev.sh
```

## Project Structure

```
canopy/
├── src/canopy/              # Main Python package
│   ├── domain/              # Core business logic
│   │   ├── strategy.py      # Strategy entities
│   │   ├── indicator.py     # Indicator definitions
│   │   ├── signal.py        # Trading signals
│   │   ├── backtest.py      # Backtest entities
│   │   └── metrics.py       # Performance metrics
│   ├── ports/               # Interface definitions
│   │   ├── data_provider.py # Data provider interface
│   │   └── backtest_engine.py # Engine interface
│   ├── application/         # Use cases
│   │   ├── run_backtest.py  # Backtest workflow
│   │   └── fetch_data.py    # Data fetching
│   ├── adapters/            # External implementations
│   │   ├── data/            # Data providers
│   │   ├── engines/         # Backtest engines
│   │   └── ui/              # CLI interface
│   ├── parser/              # DSL parser
│   │   └── parser.py
│   └── api/                 # FastAPI application
│       ├── main.py          # API entry point
│       ├── config.py        # Configuration
│       ├── routers/         # API routes
│       └── models/          # API models
├── tests/                   # Test suite
│   ├── unit/                # Unit tests
│   └── integration/         # Integration tests
├── examples/                # Example strategies
├── web/                     # React frontend
├── docs/                    # Documentation
├── scripts/                 # Helper scripts
├── docker-compose.yml       # Docker orchestration
├── Dockerfile               # Python/API Dockerfile
└── pyproject.toml          # Python dependencies
```

## Development Workflow

### 1. Create a New Branch

```bash
git checkout -b feature/my-feature
```

### 2. Make Changes

Follow TDD (Test-Driven Development):

1. Write a failing test
2. Write minimal code to pass
3. Refactor
4. Repeat

### 3. Run Tests

**All tests**:
```bash
poetry run pytest
```

**With coverage**:
```bash
poetry run pytest --cov=src/canopy --cov-report=html
```

**Specific test**:
```bash
poetry run pytest tests/unit/test_domain/test_strategy.py -v
```

**Integration tests only**:
```bash
poetry run pytest tests/integration/ -v
```

### 4. Run Linters

**Black (formatting)**:
```bash
poetry run black src/ tests/
```

**isort (import sorting)**:
```bash
poetry run isort src/ tests/
```

**flake8 (linting)**:
```bash
poetry run flake8 src/ tests/
```

**mypy (type checking)**:
```bash
poetry run mypy src/
```

**All at once**:
```bash
./scripts/test-all.sh
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: add new indicator"
```

**Commit Message Format**:
```
<type>: <description>

[optional body]

[optional footer]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance

### 6. Push and Create PR

```bash
git push origin feature/my-feature
```

Then create a Pull Request on GitHub.

## Testing

### Unit Tests

Test individual components in isolation.

**Example**:
```python
# tests/unit/test_domain/test_indicator.py
def test_sma_calculation():
    data = [1, 2, 3, 4, 5]
    result = calculate_sma(data, period=3)
    assert result == [None, None, 2.0, 3.0, 4.0]
```

### Integration Tests

Test component interactions.

**Example**:
```python
# tests/integration/test_backtest_workflow.py
def test_full_backtest():
    strategy = parser.parse(strategy_code)
    provider = YahooProvider()
    engine = SimpleEngine()

    result = run_backtest(strategy, provider, engine)

    assert result.metrics.total_return > 0
```

### Running Specific Tests

```bash
# Run tests in a specific file
poetry run pytest tests/unit/test_domain/test_strategy.py

# Run tests matching a pattern
poetry run pytest -k "test_sma"

# Run with verbose output
poetry run pytest -v

# Run with print statements
poetry run pytest -s

# Stop on first failure
poetry run pytest -x
```

### Test Coverage

```bash
# Generate HTML coverage report
poetry run pytest --cov=src/canopy --cov-report=html

# View report
open htmlcov/index.html
```

**Coverage Requirements**:
- Overall: >90%
- Domain layer: >95%
- Adapters: >80%

## Code Style

### Python

Follow PEP 8 with these additions:

- Line length: 100 characters
- Use type hints
- Use docstrings for public functions
- Use Black for formatting

**Example**:
```python
from typing import List
from canopy.domain.strategy import Strategy

def parse_strategy(code: str) -> Strategy:
    """
    Parse Canopy strategy code.

    Args:
        code: Strategy code string

    Returns:
        Parsed Strategy object

    Raises:
        SyntaxError: If code is invalid
    """
    # Implementation
    pass
```

### TypeScript/React

- Use TypeScript
- Use functional components
- Use hooks for state management
- Follow ESLint rules

**Example**:
```typescript
interface BacktestResult {
  metrics: Metrics;
  trades: Trade[];
  equityCurve: EquityPoint[];
}

const BacktestResults: React.FC<{ result: BacktestResult }> = ({ result }) => {
  return (
    <div>
      <MetricsDisplay metrics={result.metrics} />
      <TradesList trades={result.trades} />
    </div>
  );
};
```

## Adding New Features

### Adding a New Indicator

1. **Define in domain layer**:
```python
# src/canopy/domain/indicator.py
def calculate_rsi(data: List[float], period: int = 14) -> List[float]:
    """Calculate Relative Strength Index."""
    # Implementation
    pass
```

2. **Add to parser**:
```python
# src/canopy/parser/parser.py
def parse_indicator_call(self, node):
    if node.name == "rsi":
        return calculate_rsi(node.args)
```

3. **Write tests**:
```python
# tests/unit/test_domain/test_indicator.py
def test_rsi_calculation():
    data = [44, 44.34, 44.09, 43.61, 44.33]
    result = calculate_rsi(data, period=14)
    assert len(result) == len(data)
```

4. **Add documentation**:
Update `LANGUAGE_REFERENCE.md` with indicator description and examples.

5. **Add example**:
Create example strategy using the indicator.

### Adding a New Data Provider

1. **Implement interface**:
```python
# src/canopy/adapters/data/alpaca_provider.py
from canopy.ports.data_provider import IDataProvider

class AlpacaProvider(IDataProvider):
    def fetch_data(self, symbol, start_date, end_date):
        # Implementation
        pass
```

2. **Add to factory**:
```python
# src/canopy/adapters/data/provider_factory.py
def create(provider_name: str) -> IDataProvider:
    if provider_name == "alpaca":
        return AlpacaProvider()
```

3. **Write tests**:
```python
# tests/integration/test_alpaca_provider.py
def test_alpaca_fetch():
    provider = AlpacaProvider()
    data = provider.fetch_data("AAPL", "2023-01-01", "2023-12-31")
    assert len(data.bars) > 0
```

4. **Add configuration**:
Update `.env.example` with necessary API keys.

### Adding a New API Endpoint

1. **Create router function**:
```python
# src/canopy/api/routers/my_router.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/my-endpoint")
async def my_endpoint():
    return {"message": "Hello"}
```

2. **Add to main app**:
```python
# src/canopy/api/main.py
from canopy.api.routers import my_router

app.include_router(my_router.router, prefix="/api")
```

3. **Write tests**:
```python
# tests/integration/test_api.py
def test_my_endpoint(client):
    response = client.get("/api/my-endpoint")
    assert response.status_code == 200
```

4. **Update API documentation**:
Add to `API_REFERENCE.md`.

## Debugging

### Python Debugging

**Using pdb**:
```python
import pdb; pdb.set_trace()
```

**Using VS Code**:
Create `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["canopy.api.main:app", "--reload"],
      "jinja": true
    }
  ]
}
```

### Docker Debugging

**View logs**:
```bash
docker-compose logs -f canopy-api
```

**Enter container**:
```bash
docker-compose exec canopy-api bash
```

**Run tests in container**:
```bash
docker-compose exec canopy-api poetry run pytest
```

## Performance

### Profiling

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Code to profile
result = run_backtest(...)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

### Optimization Tips

1. Use vectorized operations (NumPy, Pandas)
2. Avoid loops when possible
3. Cache expensive calculations
4. Use async/await for I/O operations
5. Profile before optimizing

## Troubleshooting

### Common Issues

**Poetry install fails**:
```bash
# Clear cache
poetry cache clear pypi --all
poetry install
```

**Docker build fails**:
```bash
# Clear Docker cache
docker-compose build --no-cache
```

**Tests fail**:
```bash
# Clear pytest cache
rm -rf .pytest_cache
poetry run pytest --cache-clear
```

**Import errors**:
```bash
# Reinstall package
poetry install
```

## Pre-commit Hooks

We use pre-commit hooks to ensure code quality.

**Install hooks**:
```bash
poetry run pre-commit install
```

**Run manually**:
```bash
poetry run pre-commit run --all-files
```

**Skip hooks** (not recommended):
```bash
git commit --no-verify
```

## Continuous Integration

Our CI pipeline runs:
1. Linting (Black, isort, flake8, mypy)
2. Unit tests
3. Integration tests
4. Coverage reporting
5. Docker builds

**View CI status**: Check GitHub Actions tab

## Contributing Guidelines

1. **Fork** the repository
2. **Create** a feature branch
3. **Write** tests for new features
4. **Ensure** all tests pass
5. **Follow** code style guidelines
6. **Update** documentation
7. **Submit** a pull request

### Pull Request Checklist

- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code formatted (Black, isort)
- [ ] Type hints added
- [ ] Docstrings added
- [ ] CHANGELOG.md updated
- [ ] All CI checks pass

## Resources

- **Python**: https://docs.python.org/3/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Poetry**: https://python-poetry.org/docs/
- **Docker**: https://docs.docker.com/
- **pytest**: https://docs.pytest.org/
- **React**: https://react.dev/

## Getting Help

- **Issues**: Create a GitHub issue
- **Discussions**: Use GitHub Discussions
- **Discord**: Join our Discord server
- **Email**: dev@canopy-lang.com
