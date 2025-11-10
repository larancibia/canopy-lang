"""
Response models for API endpoints.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from canopy.api.models.schemas import (
    JobStatus,
    PerformanceMetricsSchema,
    TradeSchema,
    SignalSchema,
    OHLCVData,
)


class ErrorResponse(BaseModel):
    """Error response."""

    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Invalid strategy code",
                "detail": "Strategy must have a name: strategy \"Name\"",
                "timestamp": "2023-01-15T10:30:00Z",
            }
        }


class BacktestJobResponse(BaseModel):
    """Response for backtest job submission."""

    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Job status")
    message: str = Field(..., description="Human-readable message")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "bkt_abc123xyz",
                "status": "pending",
                "message": "Backtest job queued successfully",
                "created_at": "2023-01-15T10:30:00Z",
            }
        }


class BacktestStatusResponse(BaseModel):
    """Response for backtest job status."""

    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Job status")
    progress: Optional[float] = Field(None, description="Progress percentage (0-100)")
    message: Optional[str] = Field(None, description="Status message")
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = Field(None, description="Error message if failed")

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "bkt_abc123xyz",
                "status": "running",
                "progress": 45.5,
                "message": "Running backtest...",
                "created_at": "2023-01-15T10:30:00Z",
                "started_at": "2023-01-15T10:30:05Z",
                "completed_at": None,
                "error": None,
            }
        }


class BacktestResultResponse(BaseModel):
    """Response with complete backtest results."""

    job_id: str = Field(..., description="Job identifier")
    status: JobStatus = Field(..., description="Job status")
    strategy_name: str = Field(..., description="Strategy name")
    symbol: str = Field(..., description="Trading symbol")
    start_date: datetime = Field(..., description="Backtest start date")
    end_date: datetime = Field(..., description="Backtest end date")
    initial_capital: float = Field(..., description="Initial capital")
    final_capital: float = Field(..., description="Final capital")
    metrics: PerformanceMetricsSchema = Field(..., description="Performance metrics")
    trades: List[TradeSchema] = Field(..., description="List of trades executed")
    signals: List[SignalSchema] = Field(..., description="List of signals generated")
    equity_curve: List[Dict[str, Any]] = Field(
        ..., description="Equity curve data points"
    )
    completed_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "bkt_abc123xyz",
                "status": "completed",
                "strategy_name": "MA Crossover",
                "symbol": "AAPL",
                "start_date": "2022-01-01T00:00:00Z",
                "end_date": "2023-12-31T23:59:59Z",
                "initial_capital": 10000.0,
                "final_capital": 12534.0,
                "metrics": {
                    "total_return": 0.2534,
                    "sharpe_ratio": 1.45,
                    "sortino_ratio": 1.89,
                    "max_drawdown": -0.1234,
                    "max_drawdown_duration": 45,
                    "win_rate": 55.5,
                    "profit_factor": 1.75,
                    "calmar_ratio": 2.05,
                    "total_trades": 23,
                    "winning_trades": 13,
                    "losing_trades": 10,
                    "average_win": 523.45,
                    "average_loss": -312.89,
                },
                "trades": [],
                "signals": [],
                "equity_curve": [],
                "completed_at": "2023-01-15T10:31:00Z",
            }
        }


class StrategyParseResponse(BaseModel):
    """Response for strategy parsing."""

    success: bool = Field(..., description="Whether parsing succeeded")
    strategy_name: Optional[str] = Field(None, description="Parsed strategy name")
    indicators: Optional[Dict[str, Any]] = Field(
        None, description="Indicators defined in strategy"
    )
    buy_rules: Optional[List[str]] = Field(None, description="Buy conditions")
    sell_rules: Optional[List[str]] = Field(None, description="Sell conditions")
    error: Optional[str] = Field(None, description="Error message if parsing failed")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "strategy_name": "MA Crossover",
                "indicators": {"fast_ma": "SMA(50)", "slow_ma": "SMA(200)"},
                "buy_rules": ["crossover(fast_ma, slow_ma)"],
                "sell_rules": ["crossunder(fast_ma, slow_ma)"],
                "error": None,
            }
        }


class StrategyExampleResponse(BaseModel):
    """Response for strategy example."""

    name: str = Field(..., description="Example strategy name")
    code: str = Field(..., description="Strategy code")
    description: str = Field(..., description="Strategy description")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "MA Crossover",
                "code": 'strategy "MA Crossover"\n\nfast_ma = sma(close, 50)\nslow_ma = sma(close, 200)\n\nbuy when crossover(fast_ma, slow_ma)\nsell when crossunder(fast_ma, slow_ma)',
                "description": "Simple moving average crossover strategy",
            }
        }


class IndicatorInfoResponse(BaseModel):
    """Response for indicator information."""

    name: str = Field(..., description="Indicator name")
    description: str = Field(..., description="Indicator description")
    parameters: Dict[str, Any] = Field(..., description="Required parameters")
    example: str = Field(..., description="Usage example")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "SMA",
                "description": "Simple Moving Average",
                "parameters": {"period": "int (required, > 0)"},
                "example": "fast_ma = sma(close, 50)",
            }
        }


class IndicatorListResponse(BaseModel):
    """Response listing all available indicators."""

    indicators: List[str] = Field(..., description="List of indicator names")
    count: int = Field(..., description="Total number of indicators")

    class Config:
        json_schema_extra = {
            "example": {"indicators": ["SMA", "EMA", "RSI"], "count": 3}
        }


class DataProviderResponse(BaseModel):
    """Response for data provider information."""

    providers: List[str] = Field(..., description="Available data providers")
    default: str = Field(..., description="Default data provider")

    class Config:
        json_schema_extra = {
            "example": {"providers": ["yahoo", "csv"], "default": "yahoo"}
        }


class OHLCVResponse(BaseModel):
    """Response with OHLCV data."""

    symbol: str = Field(..., description="Trading symbol")
    start_date: datetime = Field(..., description="Start date")
    end_date: datetime = Field(..., description="End date")
    data: List[OHLCVData] = Field(..., description="OHLCV data points")
    count: int = Field(..., description="Number of data points")

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "AAPL",
                "start_date": "2022-01-01T00:00:00Z",
                "end_date": "2023-12-31T23:59:59Z",
                "data": [],
                "count": 252,
            }
        }


class SymbolSearchResponse(BaseModel):
    """Response for symbol search."""

    query: str = Field(..., description="Search query")
    results: List[str] = Field(..., description="Matching symbols")
    count: int = Field(..., description="Number of results")

    class Config:
        json_schema_extra = {
            "example": {"query": "AAPL", "results": ["AAPL", "APLE"], "count": 2}
        }
