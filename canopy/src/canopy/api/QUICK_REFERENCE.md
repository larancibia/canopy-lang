# Canopy API - Quick Reference Card

## 🚀 Start Server
```bash
cd /home/user/canopy-lang/canopy
poetry run uvicorn canopy.api.main:app --reload --port 8000
```

## 📚 Documentation URLs
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📝 Strategy Endpoints

### Parse Strategy
```bash
curl -X POST http://localhost:8000/api/strategies/parse \
  -H "Content-Type: application/json" \
  -d '{"strategy_code": "strategy \"MA Crossover\"\n..."}'
```

### Validate Strategy
```bash
curl -X POST http://localhost:8000/api/strategies/validate \
  -H "Content-Type: application/json" \
  -d '{"strategy_code": "..."}'
```

### Get Examples
```bash
curl http://localhost:8000/api/strategies/examples
curl http://localhost:8000/api/strategies/examples/ma_crossover
```

## 🔬 Backtest Endpoints

### Submit Backtest
```bash
curl -X POST http://localhost:8000/api/backtests \
  -H "Content-Type: application/json" \
  -d '{
    "strategy_code": "...",
    "symbol": "AAPL",
    "start_date": "2022-01-01T00:00:00Z",
    "end_date": "2023-12-31T23:59:59Z",
    "initial_capital": 10000.0
  }'
```

### Check Status
```bash
curl http://localhost:8000/api/backtests/{job_id}
```

### Get Results
```bash
curl http://localhost:8000/api/backtests/{job_id}/results
```

### Cancel Backtest
```bash
curl -X DELETE http://localhost:8000/api/backtests/{job_id}
```

### List Backtests
```bash
curl http://localhost:8000/api/backtests?limit=10
```

## 📊 Data Endpoints

### Get Data Providers
```bash
curl http://localhost:8000/api/data/providers
```

### Search Symbols
```bash
curl http://localhost:8000/api/data/symbols?q=AAPL
```

### Get OHLCV Data
```bash
curl "http://localhost:8000/api/data/AAPL/ohlcv?start_date=2022-01-01T00:00:00Z&end_date=2023-12-31T23:59:59Z"
```

## 📈 Indicator Endpoints

### List Indicators
```bash
curl http://localhost:8000/api/indicators
```

### Get Indicator Info
```bash
curl http://localhost:8000/api/indicators/sma
```

### Calculate Indicator
```bash
curl -X POST http://localhost:8000/api/indicators/sma/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "data": [100, 102, 101, 105, 107, 106, 108, 110, 109, 111],
    "params": {"period": 5}
  }'
```

## 🧪 Testing

### Run All Tests
```bash
poetry run pytest src/canopy/api/tests/ -v
```

### Run Specific Test File
```bash
poetry run pytest src/canopy/api/tests/test_strategies.py -v
```

### Run with Coverage
```bash
poetry run pytest src/canopy/api/tests/ --cov=canopy.api --cov-report=html
```

### Skip Slow Tests
```bash
poetry run pytest src/canopy/api/tests/ -v -m "not slow"
```

## 📋 Common Response Formats

### Success Response (Backtest Job)
```json
{
  "job_id": "bkt_abc123xyz",
  "status": "pending",
  "message": "Backtest job queued successfully",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Error Response
```json
{
  "error": "Error message",
  "detail": "Detailed information",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Backtest Results
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
    "total_trades": 23,
    ...
  },
  "trades": [...],
  "equity_curve": [...]
}
```

## ⚙️ Configuration

Edit `src/canopy/api/config.py` or set environment variables:

```bash
export API_PREFIX=/api
export ENABLE_AUTH=false
export MAX_CONCURRENT_JOBS=5
export DEFAULT_DATA_PROVIDER=yahoo
```

## 📂 Project Structure

```
src/canopy/api/
├── main.py              # FastAPI app
├── config.py            # Settings
├── dependencies.py      # DI
├── routers/             # Endpoints
├── services/            # Business logic
├── models/              # Pydantic models
├── middleware/          # CORS, errors
└── tests/               # Test suite
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
poetry run uvicorn canopy.api.main:app --port 8001
```

### Import Errors
```bash
# Reinstall dependencies
poetry install --no-cache
```

### Test Failures
```bash
# Run verbose with full output
poetry run pytest src/canopy/api/tests/ -vv --tb=long
```

## 📞 Support

- **Documentation**: http://localhost:8000/docs
- **API README**: `src/canopy/api/README.md`
- **Complete Report**: `WEB_BACKEND_API_COMPLETE.md`

---

**Quick Start**: `poetry run uvicorn canopy.api.main:app --reload`
**Documentation**: http://localhost:8000/docs
**Tests**: `poetry run pytest src/canopy/api/tests/ -v`
