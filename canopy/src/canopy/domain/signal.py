"""Signal - Buy/Sell signals"""

from enum import Enum
from datetime import datetime
from typing import Optional
import pandas as pd
from pydantic import BaseModel, Field


class SignalType(str, Enum):
    """Type of trading signal"""

    BUY = "BUY"
    SELL = "SELL"


class Signal(BaseModel):
    """
    Trading signal representation

    Indicates when to buy or sell an asset
    """

    type: SignalType = Field(..., description="Signal type (BUY or SELL)")
    timestamp: datetime = Field(..., description="When the signal occurred")
    price: float = Field(..., description="Price at which signal triggered")
    reason: Optional[str] = Field(None, description="Reason for the signal")

    def __str__(self) -> str:
        return f"{self.type.value} @ ${self.price:.2f} on {self.timestamp}"


def crossover(series1: pd.Series, series2: pd.Series) -> pd.Series:
    """
    Detect when series1 crosses above series2

    Returns:
        Boolean series where True indicates crossover
    """
    above = series1 > series2
    return above & ~above.shift(1, fill_value=False)


def crossunder(series1: pd.Series, series2: pd.Series) -> pd.Series:
    """
    Detect when series1 crosses below series2

    Returns:
        Boolean series where True indicates crossunder
    """
    below = series1 < series2
    return below & ~below.shift(1, fill_value=False)
