# Canopy Trading Language API

A comprehensive REST API for developing, testing, and running trading strategies using the Canopy domain-specific language (DSL).

## Features

- **Strategy Management**: Parse, validate, and explore example trading strategies
- **Asynchronous Backtesting**: Run backtests in the background with comprehensive metrics
- **Market Data Integration**: Fetch historical OHLCV data from multiple providers
- **Technical Indicators**: Calculate and use technical indicators (SMA, EMA, RSI, etc.)
- **Job Queue System**: Background processing with status tracking
- **OpenAPI Documentation**: Interactive API docs at `/docs`

## Quick Start

### Installation

1. Install dependencies:
```bash
cd /home/user/canopy-lang/canopy
poetry install
```

2. Start the API server:
```bash
poetry run uvicorn canopy.api.main:app --reload --port 8000
```

3. Access the interactive documentation:
```
http://localhost:8000/docs
```

### Running Tests

Run the complete test suite:
```bash
poetry run pytest src/canopy/api/tests/ -v
```

Run with coverage:
```bash
poetry run pytest src/canopy/api/tests/ --cov=canopy.api --cov-report=html
```

## Architecture

The API follows Clean Architecture and Hexagonal Architecture principles:

```
api/
├── main.py              # FastAPI application entry point
├── config.py            # Application configuration
├── dependencies.py      # Dependency injection
├── routers/             # API endpoints (controllers)
│   ├── strategies.py    # Strategy endpoints
│   ├── backtests.py     # Backtest endpoints
│   ├── data.py          # Market data endpoints
│   └── indicators.py    # Indicator endpoints
├── services/            # Business logic layer
│   ├── strategy_service.py
│   ├── backtest_service.py
│   ├── data_service.py
│   └── job_queue.py     # Background job processing
├── models/              # Request/response models
│   ├── requests.py      # Pydantic request models
│   ├── responses.py     # Pydantic response models
│   └── schemas.py       # Shared schemas
├── middleware/          # Middleware components
│   ├── cors.py          # CORS configuration
│   ├── error_handler.py # Global error handling
│   └── auth.py          # Authentication (basic)
└── tests/               # Test suite
```

## API Endpoints

### Strategy Endpoints

#### Parse Strategy
Parse Canopy strategy code and return structured information.

```bash
POST /api/strategies/parse
Content-Type: application/json

{
  "strategy_code": "strategy \"MA Crossover\"\n\nfast_ma = sma(close, 50)\nslow_ma = sma(close, 200)\n\nbuy when crossover(fast_ma, slow_ma)\nsell when crossunder(fast_ma, slow_ma)"
}
```

Response:
```json
{
  "success": true,
  "strategy_name": "MA Crossover",
  "indicators": {
    "fast_ma": "SMA(50)",
    "slow_ma": "SMA(200)"
  },
  "buy_rules": ["crossover(fast_ma, slow_ma)"],
  "sell_rules": ["crossunder(fast_ma, slow_ma)"],
  "error": null
}
```

#### Validate Strategy
Validate strategy syntax without executing.

```bash
POST /api/strategies/validate
Content-Type: application/json

{
  "strategy_code": "strategy \"MA Crossover\"\n..."
}
```

#### List Examples
Get available example strategies.

```bash
GET /api/strategies/examples
```

#### Get Example
Get specific example strategy code.

```bash
GET /api/strategies/examples/ma_crossover
```

### Backtest Endpoints

#### Submit Backtest
Submit a backtest job for asynchronous execution.

```bash
POST /api/backtests
Content-Type: application/json

{
  "strategy_code": "strategy \"MA Crossover\"\n...",
  "symbol": "AAPL",
  "start_date": "2022-01-01T00:00:00Z",
  "end_date": "2023-12-31T23:59:59Z",
  "initial_capital": 10000.0,
  "commission": 0.001,
  "slippage": 0.0,
  "data_provider": "yahoo"
}
```

Response (202 Accepted):
```json
{
  "job_id": "bkt_abc123xyz",
  "status": "pending",
  "message": "Backtest job queued successfully",
  "created_at": "2023-01-15T10:30:00Z"
}
```

#### Get Backtest Status
Check the status of a backtest job.

```bash
GET /api/backtests/{job_id}
```

Response:
```json
{
  "job_id": "bkt_abc123xyz",
  "status": "running",
  "progress": 45.5,
  "message": "Running backtest...",
  "created_at": "2023-01-15T10:30:00Z",
  "started_at": "2023-01-15T10:30:05Z",
  "completed_at": null,
  "error": null
}
```

#### Get Backtest Results
Retrieve complete backtest results (only after completion).

```bash
GET /api/backtests/{job_id}/results
```

Response:
```json
{
  "job_id": "bkt_abc123xyz",
  "status": "completed",
  "strategy_name": "MA Crossover",
  "symbol": "AAPL",
  "initial_capital": 10000.0,
  "final_capital": 12534.0,
  "metrics": {
    "total_return": 0.2534,
    "sharpe_ratio": 1.45,
    "sortino_ratio": 1.89,
    "max_drawdown": -0.1234,
    "win_rate": 55.5,
    "total_trades": 23,
    ...
  },
  "trades": [...],
  "signals": [...],
  "equity_curve": [...]
}
```

#### Cancel Backtest
Cancel a pending backtest (cannot cancel running jobs in MVP).

```bash
DELETE /api/backtests/{job_id}
```

#### List Backtests
Get list of recent backtest jobs.

```bash
GET /api/backtests?limit=100
```

### Data Endpoints

#### Get Data Providers
List available data providers.

```bash
GET /api/data/providers
```

Response:
```json
{
  "providers": ["yahoo", "csv"],
  "default": "yahoo"
}
```

#### Search Symbols
Search for trading symbols.

```bash
GET /api/data/symbols?q=AAPL
```

Response:
```json
{
  "query": "AAPL",
  "results": ["AAPL", "APLE"],
  "count": 2
}
```

#### Get OHLCV Data
Fetch historical OHLCV data.

```bash
GET /api/data/AAPL/ohlcv?start_date=2022-01-01T00:00:00Z&end_date=2023-12-31T23:59:59Z
```

Response:
```json
{
  "symbol": "AAPL",
  "start_date": "2022-01-01T00:00:00Z",
  "end_date": "2023-12-31T23:59:59Z",
  "data": [
    {
      "timestamp": "2022-01-01T00:00:00Z",
      "open": 150.25,
      "high": 152.80,
      "low": 149.50,
      "close": 151.75,
      "volume": 1234567
    },
    ...
  ],
  "count": 252
}
```

### Indicator Endpoints

#### List Indicators
Get all available technical indicators.

```bash
GET /api/indicators
```

Response:
```json
{
  "indicators": ["SMA", "EMA", "RSI"],
  "count": 3
}
```

#### Get Indicator Info
Get detailed information about an indicator.

```bash
GET /api/indicators/sma
```

Response:
```json
{
  "name": "SMA",
  "description": "Simple Moving Average - Average of closing prices over N periods",
  "parameters": {
    "period": "int (required, > 0) - Number of periods for the moving average"
  },
  "example": "fast_ma = sma(close, 50)"
}
```

#### Calculate Indicator
Calculate an indicator on provided data.

```bash
POST /api/indicators/sma/calculate
Content-Type: application/json

{
  "data": [100, 102, 101, 105, 107, 106, 108, 110, 109, 111],
  "params": {
    "period": 5
  }
}
```

Response:
```json
{
  "indicator": "SMA",
  "values": [null, null, null, null, 103.0, 104.2, 105.4, 107.2, 108.0, 108.8],
  "count": 10,
  "parameters": {"period": 5}
}
```

### Health & Status

#### Health Check
Check API health and status.

```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "job_queue": {
    "running": true,
    "workers": 5,
    "queue_size": 2,
    "total_jobs": 15
  }
}
```

## Example Workflows

### Complete Workflow Example

1. **Get an example strategy:**
```bash
curl http://localhost:8000/api/strategies/examples/ma_crossover
```

2. **Validate the strategy:**
```bash
curl -X POST http://localhost:8000/api/strategies/validate \
  -H "Content-Type: application/json" \
  -d '{"strategy_code": "strategy \"MA Crossover\"\n..."}'
```

3. **Submit a backtest:**
```bash
curl -X POST http://localhost:8000/api/backtests \
  -H "Content-Type: application/json" \
  -d '{
    "strategy_code": "strategy \"MA Crossover\"\n...",
    "symbol": "AAPL",
    "start_date": "2022-01-01T00:00:00Z",
    "end_date": "2023-12-31T23:59:59Z",
    "initial_capital": 10000.0
  }'
```

4. **Check backtest status:**
```bash
curl http://localhost:8000/api/backtests/{job_id}
```

5. **Get results:**
```bash
curl http://localhost:8000/api/backtests/{job_id}/results
```

## Configuration

Configuration is managed via `config.py` and can be overridden with environment variables:

```python
# API Settings
app_name = "Canopy Trading Language API"
api_prefix = "/api"

# CORS Settings
cors_origins = ["http://localhost:3000", "http://localhost:8080"]

# Authentication (disabled for MVP)
enable_auth = False
api_keys = ["dev-api-key-12345"]

# Job Queue
max_concurrent_jobs = 5
job_timeout_seconds = 300

# Data Provider
default_data_provider = "yahoo"
```

## Error Handling

The API uses consistent error responses:

```json
{
  "error": "Error message",
  "detail": "Detailed error information",
  "timestamp": "2023-01-15T10:30:00Z"
}
```

Common HTTP status codes:
- `200` - Success
- `202` - Accepted (async operation queued)
- `400` - Bad Request (invalid data)
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

## Performance Considerations

- **Async Operations**: All I/O operations are asynchronous
- **Background Jobs**: Long-running backtests don't block the API
- **Job Queue**: In-memory queue for MVP (use Redis in production)
- **Connection Pooling**: Data provider connections are reused
- **Rate Limiting**: Disabled for MVP (implement for production)

## Security

For MVP, authentication is disabled. For production:

1. Enable API key authentication in `config.py`
2. Set `enable_auth = True`
3. Configure API keys via environment variables
4. Use HTTPS in production
5. Implement rate limiting
6. Add request logging and monitoring

## Development

### Adding New Endpoints

1. Create router in `routers/`
2. Add business logic to `services/`
3. Define models in `models/`
4. Register router in `main.py`
5. Add tests in `tests/`

### Testing

```bash
# Run all tests
poetry run pytest src/canopy/api/tests/ -v

# Run specific test file
poetry run pytest src/canopy/api/tests/test_strategies.py -v

# Run with coverage
poetry run pytest src/canopy/api/tests/ --cov=canopy.api

# Run slow tests (integration)
poetry run pytest src/canopy/api/tests/ -v -m slow
```

## Production Deployment

Recommended production setup:

1. **ASGI Server**: Use Gunicorn with Uvicorn workers
```bash
gunicorn canopy.api.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

2. **Job Queue**: Replace in-memory queue with Redis + RQ/Celery

3. **Database**: Add PostgreSQL for job persistence

4. **Caching**: Add Redis for caching frequently accessed data

5. **Monitoring**: Add Prometheus metrics and logging

6. **Load Balancing**: Use Nginx or cloud load balancer

## Support

- Documentation: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## License

Part of the Canopy Trading Language project.
