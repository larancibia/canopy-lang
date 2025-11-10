"""
Portfolio strategies - Multi-symbol trading strategies.

This module contains portfolio strategy base classes and implementations
for pairs trading, rotation, and long-short strategies.
"""

from abc import ABC, abstractmethod
from typing import Dict, List
from pydantic import BaseModel, Field, ConfigDict
import pandas as pd
import numpy as np
from canopy.domain.timeseries import TimeSeries


class PortfolioSignal(BaseModel):
    """
    Portfolio rebalancing signal.

    Represents a signal to rebalance the portfolio to target weights.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    timestamp: pd.Timestamp = Field(..., description="Signal timestamp")
    target_weights: Dict[str, float] = Field(..., description="Target weights by symbol")
    reason: str = Field(..., description="Reason for rebalance")

    def __repr__(self):
        """String representation."""
        return f"PortfolioSignal(timestamp={self.timestamp}, weights={self.target_weights})"


class PortfolioStrategy(ABC, BaseModel):
    """
    Abstract base class for portfolio strategies.

    Portfolio strategies operate on multiple symbols and generate signals
    for portfolio rebalancing.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = Field(..., description="Strategy name")

    @abstractmethod
    def generate_signals(
        self, timeseries_data: Dict[str, TimeSeries]
    ) -> List[PortfolioSignal]:
        """
        Generate portfolio rebalancing signals.

        Args:
            timeseries_data: Dictionary mapping symbol to TimeSeries

        Returns:
            List of PortfolioSignal objects
        """
        pass


class PairsTradingStrategy(PortfolioStrategy):
    """
    Pairs trading strategy (mean reversion).

    Trades the spread between two correlated assets, going long the
    underperformer and short the outperformer when they diverge.
    """

    symbol1: str = Field(..., description="First symbol in pair")
    symbol2: str = Field(..., description="Second symbol in pair")
    lookback_period: int = Field(..., description="Lookback period for spread calculation", gt=0)
    entry_threshold: float = Field(..., description="Z-score threshold for entry", gt=0)
    exit_threshold: float = Field(..., description="Z-score threshold for exit", ge=0)

    def generate_signals(
        self, timeseries_data: Dict[str, TimeSeries]
    ) -> List[PortfolioSignal]:
        """
        Generate pairs trading signals based on spread z-score.

        Args:
            timeseries_data: Dictionary of symbol to TimeSeries

        Returns:
            List of portfolio signals
        """
        if self.symbol1 not in timeseries_data or self.symbol2 not in timeseries_data:
            return []

        ts1 = timeseries_data[self.symbol1]
        ts2 = timeseries_data[self.symbol2]

        # Calculate spread (ratio)
        spread = ts1.close / ts2.close

        # Calculate rolling z-score
        rolling_mean = spread.rolling(window=self.lookback_period).mean()
        rolling_std = spread.rolling(window=self.lookback_period).std()

        z_score = (spread - rolling_mean) / rolling_std

        signals = []
        position = None  # None, 'long_spread', or 'short_spread'

        for i in range(self.lookback_period, len(z_score)):
            current_z = z_score.iloc[i]
            timestamp = z_score.index[i]

            if pd.isna(current_z):
                continue

            # Entry signals
            if position is None:
                if current_z > self.entry_threshold:
                    # Spread too high, short spread (short symbol1, long symbol2)
                    signals.append(
                        PortfolioSignal(
                            timestamp=timestamp,
                            target_weights={self.symbol1: -0.5, self.symbol2: 0.5},
                            reason=f"Short spread (z={current_z:.2f})",
                        )
                    )
                    position = 'short_spread'
                elif current_z < -self.entry_threshold:
                    # Spread too low, long spread (long symbol1, short symbol2)
                    signals.append(
                        PortfolioSignal(
                            timestamp=timestamp,
                            target_weights={self.symbol1: 0.5, self.symbol2: -0.5},
                            reason=f"Long spread (z={current_z:.2f})",
                        )
                    )
                    position = 'long_spread'

            # Exit signals
            elif abs(current_z) < self.exit_threshold:
                # Close position
                signals.append(
                    PortfolioSignal(
                        timestamp=timestamp,
                        target_weights={self.symbol1: 0.0, self.symbol2: 0.0},
                        reason=f"Exit spread (z={current_z:.2f})",
                    )
                )
                position = None

        return signals


class RotationStrategy(PortfolioStrategy):
    """
    Rotation strategy (momentum).

    Rotates into the top N performing assets based on lookback returns.
    """

    symbols: List[str] = Field(..., description="Universe of symbols")
    lookback_period: int = Field(..., description="Lookback period for returns", gt=0)
    top_n: int = Field(..., description="Number of top performers to hold", gt=0)
    rebalance_frequency: int = Field(..., description="Rebalance frequency in days", gt=0)

    def generate_signals(
        self, timeseries_data: Dict[str, TimeSeries]
    ) -> List[PortfolioSignal]:
        """
        Generate rotation signals based on momentum.

        Args:
            timeseries_data: Dictionary of symbol to TimeSeries

        Returns:
            List of portfolio signals
        """
        # Get common dates across all symbols
        available_symbols = [s for s in self.symbols if s in timeseries_data]

        if len(available_symbols) == 0:
            return []

        # Build returns DataFrame
        returns_data = {}
        for symbol in available_symbols:
            ts = timeseries_data[symbol]
            returns_data[symbol] = ts.close.pct_change()

        returns_df = pd.DataFrame(returns_data)

        # Calculate cumulative returns over lookback period
        signals = []
        last_rebalance_idx = None

        for i in range(self.lookback_period, len(returns_df)):
            # Check if it's time to rebalance
            if last_rebalance_idx is None or (i - last_rebalance_idx) >= self.rebalance_frequency:
                # Calculate momentum (cumulative return over lookback)
                lookback_returns = returns_df.iloc[i - self.lookback_period:i].sum()

                # Sort by momentum and select top N
                top_symbols = lookback_returns.nlargest(self.top_n).index.tolist()

                # Equal weight among top N
                weight = 1.0 / self.top_n
                target_weights = {symbol: 0.0 for symbol in available_symbols}
                for symbol in top_symbols:
                    target_weights[symbol] = weight

                timestamp = returns_df.index[i]
                signals.append(
                    PortfolioSignal(
                        timestamp=timestamp,
                        target_weights=target_weights,
                        reason=f"Rotate to top {self.top_n}: {', '.join(top_symbols)}",
                    )
                )

                last_rebalance_idx = i

        return signals


class LongShortStrategy(PortfolioStrategy):
    """
    Long-short equity strategy.

    Goes long top performers and short bottom performers based on momentum.
    """

    symbols: List[str] = Field(..., description="Universe of symbols")
    lookback_period: int = Field(..., description="Lookback period for returns", gt=0)
    long_pct: float = Field(..., description="Percentage to long (e.g., 0.3 = top 30%)", gt=0, le=1.0)
    short_pct: float = Field(..., description="Percentage to short (e.g., 0.3 = bottom 30%)", gt=0, le=1.0)
    rebalance_frequency: int = Field(..., description="Rebalance frequency in days", gt=0)

    def generate_signals(
        self, timeseries_data: Dict[str, TimeSeries]
    ) -> List[PortfolioSignal]:
        """
        Generate long-short signals based on momentum.

        Args:
            timeseries_data: Dictionary of symbol to TimeSeries

        Returns:
            List of portfolio signals
        """
        # Get available symbols
        available_symbols = [s for s in self.symbols if s in timeseries_data]

        if len(available_symbols) == 0:
            return []

        # Build returns DataFrame
        returns_data = {}
        for symbol in available_symbols:
            ts = timeseries_data[symbol]
            returns_data[symbol] = ts.close.pct_change()

        returns_df = pd.DataFrame(returns_data)

        signals = []
        last_rebalance_idx = None

        for i in range(self.lookback_period, len(returns_df)):
            # Check if it's time to rebalance
            if last_rebalance_idx is None or (i - last_rebalance_idx) >= self.rebalance_frequency:
                # Calculate momentum
                lookback_returns = returns_df.iloc[i - self.lookback_period:i].sum()

                # Sort by momentum
                sorted_symbols = lookback_returns.sort_values(ascending=False).index.tolist()

                # Select long and short candidates
                n_long = max(1, int(len(sorted_symbols) * self.long_pct))
                n_short = max(1, int(len(sorted_symbols) * self.short_pct))

                long_symbols = sorted_symbols[:n_long]
                short_symbols = sorted_symbols[-n_short:]

                # Equal weight within long and short baskets
                long_weight = 0.5 / n_long  # 50% long
                short_weight = -0.5 / n_short  # 50% short

                target_weights = {symbol: 0.0 for symbol in available_symbols}
                for symbol in long_symbols:
                    target_weights[symbol] = long_weight
                for symbol in short_symbols:
                    target_weights[symbol] = short_weight

                timestamp = returns_df.index[i]
                signals.append(
                    PortfolioSignal(
                        timestamp=timestamp,
                        target_weights=target_weights,
                        reason=f"Long {len(long_symbols)}, Short {len(short_symbols)}",
                    )
                )

                last_rebalance_idx = i

        return signals


class StaticAllocationStrategy(PortfolioStrategy):
    """
    Static allocation strategy with periodic rebalancing.

    Maintains fixed target weights and rebalances periodically.
    """

    target_weights: Dict[str, float] = Field(..., description="Target allocation weights")
    rebalance_frequency: int = Field(..., description="Rebalance frequency in days", gt=0)

    def generate_signals(
        self, timeseries_data: Dict[str, TimeSeries]
    ) -> List[PortfolioSignal]:
        """
        Generate rebalancing signals to maintain target weights.

        Args:
            timeseries_data: Dictionary of symbol to TimeSeries

        Returns:
            List of portfolio signals
        """
        # Get a representative time series to determine dates
        if not timeseries_data:
            return []

        first_symbol = list(timeseries_data.keys())[0]
        dates = timeseries_data[first_symbol].close.index

        signals = []
        last_rebalance_idx = None

        for i in range(len(dates)):
            if last_rebalance_idx is None or (i - last_rebalance_idx) >= self.rebalance_frequency:
                timestamp = dates[i]
                signals.append(
                    PortfolioSignal(
                        timestamp=timestamp,
                        target_weights=self.target_weights.copy(),
                        reason="Periodic rebalance to target weights",
                    )
                )
                last_rebalance_idx = i

        return signals
