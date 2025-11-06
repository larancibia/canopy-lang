"""Strategy - Trading strategy representation"""

from abc import ABC, abstractmethod
from typing import List
from pydantic import BaseModel, Field
from canopy.domain.timeseries import TimeSeries
from canopy.domain.signal import Signal, SignalType, crossover, crossunder
from canopy.domain.indicator import SMA


class Strategy(ABC, BaseModel):
    """Base class for all trading strategies"""

    name: str = Field(..., description="Strategy name")

    @abstractmethod
    def generate_signals(self, timeseries: TimeSeries) -> List[Signal]:
        """Generate buy/sell signals from time series data"""
        pass


class MACrossoverStrategy(Strategy):
    """Simple Moving Average Crossover Strategy"""

    fast_period: int = Field(..., description="Fast MA period", gt=0)
    slow_period: int = Field(..., description="Slow MA period", gt=0)

    def generate_signals(self, timeseries: TimeSeries) -> List[Signal]:
        """Generate buy/sell signals based on MA crossover"""
        # Calculate indicators
        fast_ma = SMA(period=self.fast_period).calculate(timeseries)
        slow_ma = SMA(period=self.slow_period).calculate(timeseries)

        # Detect crossovers
        buy_signals = crossover(fast_ma, slow_ma)
        sell_signals = crossunder(fast_ma, slow_ma)

        # Convert to Signal objects
        signals = []
        for i in range(len(timeseries.close)):
            if buy_signals.iloc[i]:
                signals.append(
                    Signal(
                        type=SignalType.BUY,
                        timestamp=timeseries.close.index[i],
                        price=timeseries.close.iloc[i],
                        reason=f"Fast MA({self.fast_period}) crossed above Slow MA({self.slow_period})",
                    )
                )
            elif sell_signals.iloc[i]:
                signals.append(
                    Signal(
                        type=SignalType.SELL,
                        timestamp=timeseries.close.index[i],
                        price=timeseries.close.iloc[i],
                        reason=f"Fast MA({self.fast_period}) crossed below Slow MA({self.slow_period})",
                    )
                )

        return signals
