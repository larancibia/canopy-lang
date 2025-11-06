"""Indicator - Technical analysis indicators"""

from abc import ABC, abstractmethod
from typing import Union
import pandas as pd
import numpy as np
from pydantic import BaseModel, Field
from canopy.domain.timeseries import TimeSeries


class Indicator(ABC, BaseModel):
    """Base class for all technical indicators"""

    @abstractmethod
    def calculate(self, timeseries: TimeSeries) -> Union[pd.Series, pd.DataFrame]:
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


class MACD(Indicator):
    """
    Moving Average Convergence Divergence indicator

    MACD shows the relationship between two moving averages of a security's price.

    Formula:
    - MACD Line = 12-period EMA - 26-period EMA
    - Signal Line = 9-period EMA of MACD Line
    - Histogram = MACD Line - Signal Line
    """

    fast_period: int = Field(12, description="Fast EMA period", gt=0)
    slow_period: int = Field(26, description="Slow EMA period", gt=0)
    signal_period: int = Field(9, description="Signal line EMA period", gt=0)

    def calculate(self, timeseries: TimeSeries) -> pd.DataFrame:
        """Calculate MACD, signal line, and histogram"""
        # Calculate EMAs
        ema_fast = timeseries.close.ewm(span=self.fast_period, adjust=False).mean()
        ema_slow = timeseries.close.ewm(span=self.slow_period, adjust=False).mean()

        # MACD line
        macd_line = ema_fast - ema_slow

        # Signal line
        signal_line = macd_line.ewm(span=self.signal_period, adjust=False).mean()

        # Histogram
        histogram = macd_line - signal_line

        return pd.DataFrame({
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        })


class BollingerBands(Indicator):
    """
    Bollinger Bands indicator

    Bollinger Bands consist of a middle band (SMA) and upper/lower bands
    based on standard deviation.

    Formula:
    - Middle Band = 20-period SMA
    - Upper Band = Middle Band + (2 * standard deviation)
    - Lower Band = Middle Band - (2 * standard deviation)
    - Bandwidth = (Upper - Lower) / Middle
    - %B = (Price - Lower) / (Upper - Lower)
    """

    period: int = Field(20, description="Period for SMA and standard deviation", gt=0)
    std_dev: float = Field(2.0, description="Number of standard deviations", gt=0)

    def calculate(self, timeseries: TimeSeries) -> pd.DataFrame:
        """Calculate Bollinger Bands"""
        # Middle band (SMA)
        middle = timeseries.close.rolling(window=self.period).mean()

        # Standard deviation
        std = timeseries.close.rolling(window=self.period).std()

        # Upper and lower bands
        upper = middle + (std * self.std_dev)
        lower = middle - (std * self.std_dev)

        # Bandwidth
        bandwidth = (upper - lower) / middle

        # %B
        percent_b = (timeseries.close - lower) / (upper - lower)

        return pd.DataFrame({
            'upper': upper,
            'middle': middle,
            'lower': lower,
            'bandwidth': bandwidth,
            'percent_b': percent_b
        })


class ATR(Indicator):
    """
    Average True Range indicator

    ATR measures market volatility by decomposing the entire range of an asset price.

    Formula:
    - True Range = max[(High - Low), abs(High - Previous Close), abs(Low - Previous Close)]
    - ATR = 14-period moving average of True Range
    """

    period: int = Field(14, description="Period for ATR calculation", gt=0)

    def calculate(self, timeseries: TimeSeries) -> pd.Series:
        """Calculate ATR"""
        # Calculate True Range
        high_low = timeseries.high - timeseries.low
        high_close = np.abs(timeseries.high - timeseries.close.shift(1))
        low_close = np.abs(timeseries.low - timeseries.close.shift(1))

        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

        # ATR is the moving average of True Range
        atr = true_range.rolling(window=self.period).mean()

        return atr


class Stochastic(Indicator):
    """
    Stochastic Oscillator indicator

    The Stochastic Oscillator compares a security's closing price to its price range
    over a given time period.

    Formula:
    - %K = 100 * (Close - Lowest Low) / (Highest High - Lowest Low)
    - %D = 3-period SMA of %K
    """

    k_period: int = Field(14, description="Period for %K calculation", gt=0)
    d_period: int = Field(3, description="Period for %D smoothing", gt=0)

    def calculate(self, timeseries: TimeSeries) -> pd.DataFrame:
        """Calculate Stochastic Oscillator"""
        # Get highest high and lowest low over k_period
        lowest_low = timeseries.low.rolling(window=self.k_period).min()
        highest_high = timeseries.high.rolling(window=self.k_period).max()

        # Calculate %K
        k = 100 * (timeseries.close - lowest_low) / (highest_high - lowest_low)

        # Calculate %D (SMA of %K)
        d = k.rolling(window=self.d_period).mean()

        return pd.DataFrame({
            'k': k,
            'd': d
        })


class ADX(Indicator):
    """
    Average Directional Index indicator

    ADX measures the strength of a trend (not direction). Values above 25 indicate
    a strong trend, while values below 20 suggest a weak trend.

    Formula:
    - Calculate +DM and -DM (Directional Movement)
    - Calculate +DI and -DI (Directional Indicators)
    - Calculate DX = 100 * abs(+DI - -DI) / (+DI + -DI)
    - ADX = smoothed average of DX
    """

    period: int = Field(14, description="Period for ADX calculation", gt=0)

    def calculate(self, timeseries: TimeSeries) -> pd.Series:
        """Calculate ADX"""
        # Calculate price movements
        high_diff = timeseries.high.diff()
        low_diff = -timeseries.low.diff()

        # Calculate directional movements
        plus_dm = pd.Series(np.where((high_diff > low_diff) & (high_diff > 0), high_diff, 0),
                           index=timeseries.index)
        minus_dm = pd.Series(np.where((low_diff > high_diff) & (low_diff > 0), low_diff, 0),
                            index=timeseries.index)

        # Calculate True Range (same as ATR)
        high_low = timeseries.high - timeseries.low
        high_close = np.abs(timeseries.high - timeseries.close.shift(1))
        low_close = np.abs(timeseries.low - timeseries.close.shift(1))
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

        # Smooth the values
        atr = true_range.rolling(window=self.period).mean()
        plus_di = 100 * (plus_dm.rolling(window=self.period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=self.period).mean() / atr)

        # Calculate DX
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)

        # ADX is the smoothed average of DX
        adx = dx.rolling(window=self.period).mean()

        return adx


class OBV(Indicator):
    """
    On-Balance Volume indicator

    OBV is a cumulative volume-based indicator that adds volume on up days
    and subtracts volume on down days.

    Formula:
    - If Close > Previous Close: OBV = Previous OBV + Volume
    - If Close < Previous Close: OBV = Previous OBV - Volume
    - If Close = Previous Close: OBV = Previous OBV
    """

    def calculate(self, timeseries: TimeSeries) -> pd.Series:
        """Calculate On-Balance Volume"""
        # Determine price direction
        price_change = timeseries.close.diff()

        # Create volume direction: +1 for up, -1 for down, 0 for unchanged
        volume_direction = pd.Series(np.where(price_change > 0, 1,
                                             np.where(price_change < 0, -1, 0)),
                                    index=timeseries.index)

        # Calculate signed volume
        signed_volume = volume_direction * timeseries.volume

        # OBV is cumulative sum
        obv = signed_volume.cumsum()

        return obv


class VWAP(Indicator):
    """
    Volume Weighted Average Price indicator

    VWAP is the average price weighted by volume. It's often used as a
    benchmark for execution quality.

    Formula:
    - Typical Price = (High + Low + Close) / 3
    - VWAP = Cumulative(Typical Price * Volume) / Cumulative(Volume)
    """

    def calculate(self, timeseries: TimeSeries) -> pd.Series:
        """Calculate VWAP"""
        # Calculate typical price
        typical_price = (timeseries.high + timeseries.low + timeseries.close) / 3

        # Calculate cumulative typical price * volume
        cumulative_tpv = (typical_price * timeseries.volume).cumsum()

        # Calculate cumulative volume
        cumulative_volume = timeseries.volume.cumsum()

        # VWAP
        vwap = cumulative_tpv / cumulative_volume

        return vwap


class ParabolicSAR(Indicator):
    """
    Parabolic SAR (Stop and Reverse) indicator

    Parabolic SAR is a trend-following indicator that provides entry and exit points.
    The SAR appears as dots above or below price, indicating potential reversals.

    Formula:
    - SAR = Prior SAR + Prior AF * (Prior EP - Prior SAR)
    - AF (Acceleration Factor) starts at 0.02 and increases by 0.02 each period
      the extreme point makes a new high/low, up to a maximum of 0.2
    """

    acceleration: float = Field(0.02, description="Acceleration factor step", gt=0)
    maximum: float = Field(0.2, description="Maximum acceleration factor", gt=0)

    def calculate(self, timeseries: TimeSeries) -> pd.Series:
        """Calculate Parabolic SAR"""
        length = len(timeseries)
        sar = pd.Series(index=timeseries.index, dtype=float)

        if length < 2:
            return sar

        # Initialize
        is_uptrend = True
        af = self.acceleration
        extreme_point = timeseries.high.iloc[0]
        sar.iloc[0] = timeseries.low.iloc[0]

        for i in range(1, length):
            # Calculate SAR
            sar.iloc[i] = sar.iloc[i-1] + af * (extreme_point - sar.iloc[i-1])

            # Check for trend reversal
            if is_uptrend:
                # In uptrend, SAR should be below price
                if sar.iloc[i] > timeseries.low.iloc[i]:
                    is_uptrend = False
                    sar.iloc[i] = extreme_point
                    extreme_point = timeseries.low.iloc[i]
                    af = self.acceleration
                else:
                    # Update extreme point and AF
                    if timeseries.high.iloc[i] > extreme_point:
                        extreme_point = timeseries.high.iloc[i]
                        af = min(af + self.acceleration, self.maximum)
            else:
                # In downtrend, SAR should be above price
                if sar.iloc[i] < timeseries.high.iloc[i]:
                    is_uptrend = True
                    sar.iloc[i] = extreme_point
                    extreme_point = timeseries.high.iloc[i]
                    af = self.acceleration
                else:
                    # Update extreme point and AF
                    if timeseries.low.iloc[i] < extreme_point:
                        extreme_point = timeseries.low.iloc[i]
                        af = min(af + self.acceleration, self.maximum)

        return sar


class CCI(Indicator):
    """
    Commodity Channel Index indicator

    CCI measures the difference between a security's price and its average price.
    High values indicate overbought conditions, low values indicate oversold.

    Formula:
    - Typical Price = (High + Low + Close) / 3
    - SMA = 20-period moving average of Typical Price
    - Mean Deviation = Mean absolute deviation of Typical Price from SMA
    - CCI = (Typical Price - SMA) / (0.015 * Mean Deviation)
    """

    period: int = Field(20, description="Period for CCI calculation", gt=0)

    def calculate(self, timeseries: TimeSeries) -> pd.Series:
        """Calculate CCI"""
        # Calculate typical price
        typical_price = (timeseries.high + timeseries.low + timeseries.close) / 3

        # Calculate SMA of typical price
        sma = typical_price.rolling(window=self.period).mean()

        # Calculate mean absolute deviation
        mad = typical_price.rolling(window=self.period).apply(
            lambda x: np.abs(x - x.mean()).mean(), raw=True
        )

        # Calculate CCI
        cci = (typical_price - sma) / (0.015 * mad)

        return cci


class WilliamsR(Indicator):
    """
    Williams %R indicator

    Williams %R is a momentum indicator that measures overbought/oversold levels.
    It's the inverse of the Stochastic Oscillator.

    Formula:
    - %R = -100 * (Highest High - Close) / (Highest High - Lowest Low)
    - Values range from -100 (oversold) to 0 (overbought)
    """

    period: int = Field(14, description="Period for Williams %R calculation", gt=0)

    def calculate(self, timeseries: TimeSeries) -> pd.Series:
        """Calculate Williams %R"""
        # Get highest high and lowest low over period
        highest_high = timeseries.high.rolling(window=self.period).max()
        lowest_low = timeseries.low.rolling(window=self.period).min()

        # Calculate Williams %R
        williams_r = -100 * (highest_high - timeseries.close) / (highest_high - lowest_low)

        return williams_r
