"""
Request models for API endpoints.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class BacktestRequest(BaseModel):
    """Request to run a backtest."""

    strategy_code: str = Field(
        ..., description="Canopy strategy code", min_length=1, max_length=50000
    )
    symbol: str = Field(..., description="Trading symbol (e.g., AAPL, MSFT)", min_length=1)
    start_date: datetime = Field(..., description="Backtest start date")
    end_date: datetime = Field(..., description="Backtest end date")
    initial_capital: Optional[float] = Field(
        10000.0, description="Initial capital", gt=0
    )
    commission: Optional[float] = Field(
        0.001, description="Commission per trade as decimal (0.001 = 0.1%)", ge=0
    )
    slippage: Optional[float] = Field(
        0.0, description="Slippage per trade as decimal", ge=0
    )
    data_provider: Optional[str] = Field(
        "yahoo", description="Data provider to use (yahoo, csv)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "strategy_code": 'strategy "MA Crossover"\n\nfast_ma = sma(close, 50)\nslow_ma = sma(close, 200)\n\nbuy when crossover(fast_ma, slow_ma)\nsell when crossunder(fast_ma, slow_ma)',
                "symbol": "AAPL",
                "start_date": "2022-01-01T00:00:00Z",
                "end_date": "2023-12-31T23:59:59Z",
                "initial_capital": 10000.0,
                "commission": 0.001,
                "slippage": 0.0,
                "data_provider": "yahoo",
            }
        }


class StrategyParseRequest(BaseModel):
    """Request to parse strategy code."""

    strategy_code: str = Field(
        ..., description="Canopy strategy code to parse", min_length=1, max_length=50000
    )

    class Config:
        json_schema_extra = {
            "example": {
                "strategy_code": 'strategy "MA Crossover"\n\nfast_ma = sma(close, 50)\nslow_ma = sma(close, 200)\n\nbuy when crossover(fast_ma, slow_ma)\nsell when crossunder(fast_ma, slow_ma)'
            }
        }


class StrategyValidateRequest(BaseModel):
    """Request to validate strategy syntax."""

    strategy_code: str = Field(
        ..., description="Canopy strategy code to validate", min_length=1, max_length=50000
    )

    class Config:
        json_schema_extra = {
            "example": {
                "strategy_code": 'strategy "MA Crossover"\n\nfast_ma = sma(close, 50)\nslow_ma = sma(close, 200)\n\nbuy when crossover(fast_ma, slow_ma)\nsell when crossunder(fast_ma, slow_ma)'
            }
        }


class IndicatorCalculateRequest(BaseModel):
    """Request to calculate an indicator."""

    data: List[float] = Field(..., description="Price data for calculation")
    params: Optional[Dict[str, Any]] = Field(
        None, description="Indicator parameters (e.g., period)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "data": [100, 102, 101, 105, 107, 106, 108, 110, 109, 111],
                "params": {"period": 5},
            }
        }
