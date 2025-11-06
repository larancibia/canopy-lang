"""Indicator - Technical analysis indicators"""

from abc import ABC, abstractmethod
import pandas as pd
from pydantic import BaseModel, Field
from canopy.domain.timeseries import TimeSeries


class Indicator(ABC, BaseModel):
    """Base class for all technical indicators"""

    @abstractmethod
    def calculate(self, timeseries: TimeSeries) -> pd.Series:
        """Calculate indicator values"""
        pass


class SMA(Indicator):
    """Simple Moving Average indicator"""

    period: int = Field(..., description="Number of periods for moving average", gt=0)

    def calculate(self, timeseries: TimeSeries) -> pd.Series:
        """Calculate SMA"""
        return timeseries.close.rolling(window=self.period).mean()


class EMA(Indicator):
    """Exponential Moving Average indicator"""

    period: int = Field(..., description="Number of periods for moving average", gt=0)

    def calculate(self, timeseries: TimeSeries) -> pd.Series:
        """Calculate EMA"""
        return timeseries.close.ewm(span=self.period, adjust=False).mean()


class RSI(Indicator):
    """Relative Strength Index indicator"""

    period: int = Field(14, description="Number of periods for RSI", gt=0)

    def calculate(self, timeseries: TimeSeries) -> pd.Series:
        """Calculate RSI"""
        delta = timeseries.close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
