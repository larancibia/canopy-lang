# Canopy API Reference

## Base URL

```
Development: http://localhost:8000
Production: https://api.canopy-lang.com
```

## Authentication

Currently, authentication is disabled for MVP. Future versions will support:
- API Key authentication
- JWT tokens
- OAuth 2.0

## Endpoints

### Health Check

#### GET /health

Check API health status.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T12:00:00Z",
  "service": "canopy-api"
}
```

#### GET /health/readiness

Check if service is ready to accept requests.

**Response**:
```json
{
  "ready": true,
  "timestamp": "2024-01-15T12:00:00Z",
  "checks": {
    "database": "ok",
    "redis": "ok",
    "data_providers": "ok"
  }
}
```

---

### Strategies

#### POST /api/strategies/parse

Parse and validate a Canopy strategy.

**Request Body**:
```json
{
  "strategy_code": "strategy \"MA Crossover\"\nfast_ma = sma(close, 50)\nslow_ma = sma(close, 200)\nbuy when crossover(fast_ma, slow_ma)\nsell when crossunder(fast_ma, slow_ma)",
  "validate": true
}
```

**Response**:
```json
{
  "success": true,
  "strategy_name": "MA Crossover",
  "indicators": ["sma", "sma"],
  "signals": ["BUY", "SELL"],
  "plots": ["fast_ma", "slow_ma"],
  "errors": []
}
```

**Error Response**:
```json
{
  "success": false,
  "errors": ["Syntax error on line 5: unexpected token 'when'"]
}
```

#### POST /api/strategies/validate

Quick validation without full parsing.

**Request Body**:
```json
{
  "strategy_code": "strategy \"My Strategy\"..."
}
```

**Response**:
```json
{
  "valid": true,
  "strategy_name": "My Strategy",
  "indicators_count": 3,
  "signals_count": 2
}
```

#### GET /api/strategies/examples

Get list of example strategies.

**Response**:
```json
{
  "examples": [
    {
      "name": "MA Crossover",
      "description": "Simple moving average crossover strategy",
      "file": "ma_crossover.canopy",
      "difficulty": "beginner"
    }
  ],
  "count": 1
}
```

---

### Backtests

#### POST /api/backtests/run

Submit a backtest job.

**Request Body**:
```json
{
  "strategy_code": "strategy \"MA Crossover\"...",
  "symbol": "AAPL",
  "start_date": "2022-01-01",
  "end_date": "2023-12-31",
  "initial_capital": 10000.0,
  "commission": 0.001,
  "provider": "yahoo"
}
```

**Response**:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "Backtest job submitted successfully"
}
```

#### GET /api/backtests/{job_id}

Get backtest results by job ID.

**Response (Pending)**:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running"
}
```

**Response (Completed)**:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "strategy_name": "MA Crossover",
  "symbol": "AAPL",
  "start_date": "2022-01-01",
  "end_date": "2023-12-31",
  "metrics": {
    "total_return": 0.2534,
    "sharpe_ratio": 1.45,
    "sortino_ratio": 1.89,
    "max_drawdown": -0.1234,
    "win_rate": 55.5,
    "profit_factor": 1.75,
    "total_trades": 23
  },
  "trades": [
    {
      "entry_date": "2022-03-15T00:00:00Z",
      "exit_date": "2022-05-20T00:00:00Z",
      "entry_price": 150.25,
      "exit_price": 165.50,
      "shares": 100,
      "pnl": 1525.0,
      "return_pct": 10.15
    }
  ],
  "equity_curve": [
    {
      "date": "2022-01-01T00:00:00Z",
      "equity": 10000.0
    },
    {
      "date": "2022-01-02T00:00:00Z",
      "equity": 10050.0
    }
  ]
}
```

**Response (Failed)**:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "failed",
  "error": "Symbol INVALID not found"
}
```

#### GET /api/backtests

List all backtest jobs.

**Response**:
```json
{
  "jobs": [
    {
      "job_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "completed",
      "created_at": "2024-01-15T12:00:00Z"
    }
  ],
  "count": 1
}
```

#### DELETE /api/backtests/{job_id}

Delete a backtest job.

**Response**:
```json
{
  "message": "Backtest deleted successfully",
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

### Market Data

#### POST /api/data/fetch

Fetch historical market data.

**Request Body**:
```json
{
  "symbol": "AAPL",
  "start_date": "2022-01-01",
  "end_date": "2023-12-31",
  "provider": "yahoo"
}
```

**Response**:
```json
{
  "symbol": "AAPL",
  "start_date": "2022-01-01",
  "end_date": "2023-12-31",
  "data_points": 252,
  "data": [
    {
      "timestamp": "2022-01-03T00:00:00Z",
      "open": 177.83,
      "high": 182.88,
      "low": 177.71,
      "close": 182.01,
      "volume": 104487900
    }
  ]
}
```

#### GET /api/data/providers

List available data providers.

**Response**:
```json
{
  "providers": [
    {
      "name": "yahoo",
      "description": "Yahoo Finance (free, no API key required)",
      "supported_assets": ["stocks", "etfs", "indices"],
      "rate_limits": "2000 requests/hour",
      "data_quality": "high"
    }
  ],
  "count": 1
}
```

#### GET /api/data/symbols?query=AAPL

Search for trading symbols.

**Query Parameters**:
- `query` (optional): Search term

**Response**:
```json
{
  "symbols": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "exchange": "NASDAQ"
    }
  ],
  "count": 1
}
```

---

### Indicators

#### GET /api/indicators/list

List all available technical indicators.

**Response**:
```json
{
  "indicators": [
    {
      "name": "sma",
      "description": "Simple Moving Average",
      "parameters": [
        {
          "name": "data",
          "type": "series",
          "description": "Input data series"
        },
        {
          "name": "period",
          "type": "int",
          "description": "Period length"
        }
      ],
      "example": "sma(close, 20)",
      "category": "trend"
    }
  ],
  "categories": {
    "trend": [...],
    "momentum": [...],
    "volatility": [...]
  },
  "total_count": 15
}
```

#### GET /api/indicators/{indicator_name}

Get detailed information about a specific indicator.

**Response**:
```json
{
  "name": "sma",
  "description": "Simple Moving Average - The average price over a specified period",
  "parameters": [
    {
      "name": "data",
      "type": "series",
      "description": "Input data series"
    },
    {
      "name": "period",
      "type": "int",
      "description": "Period length"
    }
  ],
  "example": "fast_ma = sma(close, 50)\nslow_ma = sma(close, 200)",
  "category": "trend"
}
```

#### GET /api/indicators/categories/list

List indicator categories.

**Response**:
```json
{
  "categories": [
    {
      "name": "trend",
      "description": "Trend-following indicators",
      "examples": ["SMA", "EMA", "ADX"]
    }
  ],
  "count": 4
}
```

---

## Error Responses

### Standard Error Format

```json
{
  "detail": "Error message",
  "type": "error_type",
  "message": "Detailed explanation"
}
```

### HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error)
- `404` - Not Found
- `429` - Too Many Requests (rate limited)
- `500` - Internal Server Error

## Rate Limiting

**Current MVP**: No rate limiting

**Future**:
- 60 requests per minute per IP
- 1000 requests per hour per API key
- Header: `X-RateLimit-Remaining`

## Pagination

**Future**: For endpoints returning lists

```
GET /api/backtests?page=1&limit=20
```

**Response Headers**:
```
X-Total-Count: 100
X-Page: 1
X-Per-Page: 20
```

## WebSocket API (Future)

### Connect

```javascript
ws://localhost:8000/ws/backtests/{job_id}
```

### Real-time Updates

```json
{
  "type": "progress",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "progress": 45,
  "message": "Processing data..."
}
```

## SDK Examples

### Python

```python
import requests

# Parse strategy
response = requests.post(
    "http://localhost:8000/api/strategies/parse",
    json={
        "strategy_code": "strategy \"My Strategy\"...",
        "validate": True
    }
)
result = response.json()

# Run backtest
response = requests.post(
    "http://localhost:8000/api/backtests/run",
    json={
        "strategy_code": "...",
        "symbol": "AAPL",
        "start_date": "2022-01-01",
        "end_date": "2023-12-31"
    }
)
job = response.json()
job_id = job["job_id"]

# Get results
response = requests.get(f"http://localhost:8000/api/backtests/{job_id}")
results = response.json()
```

### JavaScript

```javascript
// Parse strategy
const response = await fetch("http://localhost:8000/api/strategies/parse", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    strategy_code: "strategy \"My Strategy\"...",
    validate: true
  })
});
const result = await response.json();

// Run backtest
const backtestResponse = await fetch("http://localhost:8000/api/backtests/run", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    strategy_code: "...",
    symbol: "AAPL",
    start_date: "2022-01-01",
    end_date: "2023-12-31"
  })
});
const job = await backtestResponse.json();

// Poll for results
const resultsResponse = await fetch(`http://localhost:8000/api/backtests/${job.job_id}`);
const results = await resultsResponse.json();
```

## Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json
