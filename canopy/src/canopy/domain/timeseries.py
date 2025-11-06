"""TimeSeries - Price data representation"""

from typing import Union
import pandas as pd
from pydantic import BaseModel, Field, model_validator


class TimeSeries(BaseModel):
    """
    Time series data for trading strategies

    Represents OHLCV (Open, High, Low, Close, Volume) data
    """

    model_config = {"arbitrary_types_allowed": True}

    open: pd.Series = Field(..., description="Opening prices")
    high: pd.Series = Field(..., description="High prices")
    low: pd.Series = Field(..., description="Low prices")
    close: pd.Series = Field(..., description="Closing prices")
    volume: pd.Series = Field(..., description="Trading volume")

    @model_validator(mode='after')
    def validate_data(self) -> 'TimeSeries':
        """Validate that OHLCV data is consistent"""
        # Check all series have same length
        lengths = [len(self.open), len(self.high), len(self.low),
                   len(self.close), len(self.volume)]
        if len(set(lengths)) != 1:
            raise ValueError("All series must have the same length")

        # Skip validation for empty series
        if len(self.close) == 0:
            return self

        # Check high >= low
        if not (self.high >= self.low).all():
            raise ValueError("High must be >= Low")

        return self

    def __len__(self) -> int:
        """Return number of data points"""
        return len(self.close)

    @property
    def index(self):
        """Get the datetime index from the close series"""
        return self.close.index

    def __getitem__(self, key: Union[int, slice]) -> Union[dict[str, float], 'TimeSeries']:
        """
        Allow indexing and slicing.

        For single index: returns dict with OHLCV values
        For slice: returns new TimeSeries
        """
        if isinstance(key, slice):
            return TimeSeries(
                open=self.open.iloc[key],
                high=self.high.iloc[key],
                low=self.low.iloc[key],
                close=self.close.iloc[key],
                volume=self.volume.iloc[key]
            )
        else:
            # Single item access - return dict
            return {
                "open": self.open.iloc[key],
                "high": self.high.iloc[key],
                "low": self.low.iloc[key],
                "close": self.close.iloc[key],
                "volume": self.volume.iloc[key],
            }

    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert TimeSeries to DataFrame.

        Returns:
            pd.DataFrame with columns [open, high, low, close, volume]
        """
        return pd.DataFrame({
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
        })

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame) -> "TimeSeries":
        """
        Create TimeSeries from DataFrame

        Args:
            df: DataFrame with columns: open, high, low, close, volume
        """
        return cls(
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            volume=df["volume"],
        )
