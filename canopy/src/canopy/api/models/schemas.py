"""
Common schemas used across the API.
"""

from enum import Enum
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    """Status of a background job."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PerformanceMetricsSchema(BaseModel):
    """Performance metrics from a backtest."""

    total_return: float = Field(..., description="Total return as decimal (e.g., 0.25 = 25%)")
    sharpe_ratio: float = Field(..., description="Sharpe ratio")
    sortino_ratio: float = Field(..., description="Sortino ratio")
    max_drawdown: float = Field(..., description="Maximum drawdown as decimal")
    max_drawdown_duration: int = Field(..., description="Max drawdown duration in days")
    win_rate: float = Field(..., description="Percentage of winning trades")
    profit_factor: float = Field(..., description="Ratio of gross profit to gross loss")
    calmar_ratio: float = Field(..., description="Calmar ratio (return/max drawdown)")
    total_trades: int = Field(..., description="Total number of trades")
    winning_trades: int = Field(..., description="Number of winning trades")
    losing_trades: int = Field(..., description="Number of losing trades")
    average_win: float = Field(..., description="Average winning trade P&L")
    average_loss: float = Field(..., description="Average losing trade P&L")

    class Config:
        json_schema_extra = {
            "example": {
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
            }
        }


class TradeSchema(BaseModel):
    """Trade details."""

    entry_date: datetime = Field(..., description="Entry timestamp")
    exit_date: datetime = Field(..., description="Exit timestamp")
    entry_price: float = Field(..., description="Entry price")
    exit_price: float = Field(..., description="Exit price")
    shares: float = Field(..., description="Number of shares")
    pnl: float = Field(..., description="Profit/Loss")
    return_pct: float = Field(..., description="Return percentage")

    class Config:
        json_schema_extra = {
            "example": {
                "entry_date": "2023-01-15T00:00:00Z",
                "exit_date": "2023-02-20T00:00:00Z",
                "entry_price": 150.25,
                "exit_price": 165.50,
                "shares": 100,
                "pnl": 1525.0,
                "return_pct": 10.15,
            }
        }


class SignalSchema(BaseModel):
    """Trading signal details."""

    type: str = Field(..., description="Signal type (BUY or SELL)")
    timestamp: datetime = Field(..., description="Signal timestamp")
    price: float = Field(..., description="Price at signal")
    reason: Optional[str] = Field(None, description="Signal reason/description")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "BUY",
                "timestamp": "2023-01-15T00:00:00Z",
                "price": 150.25,
                "reason": "Fast MA(50) crossed above Slow MA(200)",
            }
        }


class OHLCVData(BaseModel):
    """OHLCV candlestick data."""

    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2023-01-15T00:00:00Z",
                "open": 150.25,
                "high": 152.80,
                "low": 149.50,
                "close": 151.75,
                "volume": 1234567,
            }
        }
