"""
Backtest domain entity - Pure business logic for backtesting results.

This module contains the core domain models for backtest results,
following hexagonal architecture principles (no external dependencies).
"""

from typing import List
from pydantic import BaseModel, field_validator, ConfigDict
import pandas as pd


class Trade(BaseModel):
    """
    Represents a single trade.

    A trade captures the complete lifecycle of a position from entry to exit,
    including all relevant metrics like P&L and returns.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    entry_time: pd.Timestamp
    exit_time: pd.Timestamp
    entry_price: float
    exit_price: float
    quantity: float
    side: str  # "long" or "short"
    pnl: float
    return_pct: float

    @field_validator('side')
    @classmethod
    def validate_side(cls, v: str) -> str:
        """Validate that side is either 'long' or 'short'"""
        if v not in ['long', 'short']:
            raise ValueError("Side must be 'long' or 'short'")
        return v


class Backtest(BaseModel):
    """
    Backtest results container.

    Contains all results from a backtest execution including equity curve,
    trades, and metadata about the strategy and capital.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    strategy_name: str
    initial_capital: float
    equity_curve: pd.Series
    trades: List[Trade]

    @field_validator('initial_capital')
    @classmethod
    def validate_capital(cls, v: float) -> float:
        """Validate that initial capital is positive"""
        if v <= 0:
            raise ValueError("Initial capital must be positive")
        return v

    def total_return(self) -> float:
        """
        Calculate total return percentage.

        Returns:
            Total return as a percentage (e.g., 3.0 for 3%)
        """
        if len(self.equity_curve) == 0:
            return 0.0
        final = self.equity_curve.iloc[-1]
        return ((final - self.initial_capital) / self.initial_capital) * 100.0

    def final_equity(self) -> float:
        """
        Get final equity value.

        Returns:
            Final equity value from the equity curve
        """
        if len(self.equity_curve) == 0:
            return self.initial_capital
        return float(self.equity_curve.iloc[-1])
