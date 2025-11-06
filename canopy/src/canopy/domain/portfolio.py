"""
Portfolio domain models - Pure business logic for portfolio management.

This module contains core domain models for portfolio management including
positions, portfolio container, position sizing strategies, and rebalancing logic.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
import pandas as pd
import numpy as np


class Position(BaseModel):
    """
    Represents a single position in a portfolio.

    A position captures all information about holding a specific symbol including
    quantity, entry price, and entry time.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    symbol: str = Field(..., description="Symbol identifier (e.g., 'AAPL')")
    quantity: float = Field(..., description="Number of shares/contracts", gt=0)
    entry_price: float = Field(..., description="Price at entry", gt=0)
    entry_time: pd.Timestamp = Field(..., description="Timestamp of entry")

    def market_value(self, current_price: float) -> float:
        """
        Calculate current market value of the position.

        Args:
            current_price: Current market price

        Returns:
            Market value (quantity * current_price)
        """
        return self.quantity * current_price

    def pnl(self, current_price: float) -> float:
        """
        Calculate profit/loss on the position.

        Args:
            current_price: Current market price

        Returns:
            P&L in dollars
        """
        return (current_price - self.entry_price) * self.quantity

    def return_pct(self, current_price: float) -> float:
        """
        Calculate return percentage on the position.

        Args:
            current_price: Current market price

        Returns:
            Return as a percentage (e.g., 10.5 for 10.5%)
        """
        return ((current_price - self.entry_price) / self.entry_price) * 100.0


class Portfolio(BaseModel):
    """
    Portfolio container managing multiple positions.

    Tracks cash balance, positions across multiple symbols, and provides
    methods for calculating total portfolio value and P&L.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    initial_capital: float = Field(..., description="Starting capital", gt=0)
    positions: Dict[str, Position] = Field(
        default_factory=dict, description="Map of symbol to Position"
    )
    cash: float = Field(..., description="Available cash balance", ge=0)

    @field_validator("initial_capital")
    @classmethod
    def validate_capital(cls, v: float) -> float:
        """Validate that initial capital is positive."""
        if v <= 0:
            raise ValueError("Initial capital must be positive")
        return v

    def add_position(self, position: Position) -> None:
        """
        Add a position to the portfolio.

        Updates cash balance by deducting the cost of the position.

        Args:
            position: Position to add

        Raises:
            ValueError: If insufficient cash
        """
        cost = position.quantity * position.entry_price

        if cost > self.cash:
            raise ValueError(f"Insufficient cash: need {cost}, have {self.cash}")

        self.positions[position.symbol] = position
        self.cash -= cost

    def remove_position(self, symbol: str, exit_price: float) -> Position:
        """
        Remove a position from the portfolio.

        Updates cash balance by adding the proceeds from selling.

        Args:
            symbol: Symbol to remove
            exit_price: Exit price for the position

        Returns:
            The removed Position

        Raises:
            KeyError: If symbol not in portfolio
        """
        if symbol not in self.positions:
            raise KeyError(f"Symbol {symbol} not in portfolio")

        position = self.positions[symbol]
        proceeds = position.quantity * exit_price
        self.cash += proceeds

        del self.positions[symbol]
        return position

    def total_value(self, current_prices: Dict[str, float]) -> float:
        """
        Calculate total portfolio value.

        Args:
            current_prices: Map of symbol to current price

        Returns:
            Total portfolio value (cash + market value of all positions)
        """
        positions_value = sum(
            position.market_value(current_prices[symbol])
            for symbol, position in self.positions.items()
            if symbol in current_prices
        )

        return self.cash + positions_value

    def total_pnl(self, current_prices: Dict[str, float]) -> float:
        """
        Calculate total unrealized P&L across all positions.

        Args:
            current_prices: Map of symbol to current price

        Returns:
            Total unrealized P&L
        """
        return sum(
            position.pnl(current_prices[symbol])
            for symbol, position in self.positions.items()
            if symbol in current_prices
        )

    def get_weights(self, current_prices: Dict[str, float]) -> Dict[str, float]:
        """
        Get current portfolio weights.

        Args:
            current_prices: Map of symbol to current price

        Returns:
            Map of symbol to weight (0.0 to 1.0)
        """
        total_val = self.total_value(current_prices)

        if total_val == 0:
            return {}

        return {
            symbol: position.market_value(current_prices[symbol]) / total_val
            for symbol, position in self.positions.items()
            if symbol in current_prices
        }


class PositionSizer(ABC):
    """
    Abstract base class for position sizing strategies.

    Position sizers determine how much capital to allocate to each position
    in the portfolio based on various criteria.
    """

    @abstractmethod
    def calculate_weights(
        self,
        symbols: list[str],
        prices: Dict[str, float],
        capital: float,
        returns: Optional[pd.DataFrame] = None,
        **kwargs
    ) -> Dict[str, float]:
        """
        Calculate position weights for each symbol.

        Args:
            symbols: List of symbols to size
            prices: Current prices for each symbol
            capital: Total capital to allocate
            returns: Optional historical returns DataFrame
            **kwargs: Additional parameters

        Returns:
            Map of symbol to weight (weights should sum to 1.0)
        """
        pass


class EqualWeightSizer(PositionSizer):
    """
    Equal weight position sizing.

    Allocates equal capital to each position regardless of any other factors.
    """

    def __init__(self, num_positions: int):
        """
        Initialize equal weight sizer.

        Args:
            num_positions: Number of positions to hold
        """
        self.num_positions = num_positions

    def calculate_weights(
        self,
        symbols: list[str],
        prices: Dict[str, float],
        capital: float,
        returns: Optional[pd.DataFrame] = None,
        **kwargs
    ) -> Dict[str, float]:
        """
        Calculate equal weights for all symbols.

        Args:
            symbols: List of symbols
            prices: Current prices (not used)
            capital: Total capital (not used)
            returns: Historical returns (not used)

        Returns:
            Equal weights for all symbols
        """
        weight = 1.0 / len(symbols)
        return {symbol: weight for symbol in symbols}


class RiskParitySizer(PositionSizer):
    """
    Risk parity position sizing.

    Allocates capital inversely proportional to volatility, so each position
    contributes equal risk to the portfolio.
    """

    def calculate_weights(
        self,
        symbols: list[str],
        prices: Dict[str, float],
        capital: float,
        returns: Optional[pd.DataFrame] = None,
        **kwargs
    ) -> Dict[str, float]:
        """
        Calculate risk parity weights.

        Args:
            symbols: List of symbols
            prices: Current prices
            capital: Total capital
            returns: Historical returns DataFrame (required)

        Returns:
            Risk parity weights

        Raises:
            ValueError: If returns data is not provided
        """
        if returns is None or returns.empty:
            raise ValueError("Risk parity sizing requires returns data")

        # Calculate volatilities
        volatilities = returns[symbols].std()

        # Inverse volatility weighting
        inv_vol = 1.0 / volatilities
        weights_array = inv_vol / inv_vol.sum()

        return {symbol: float(weights_array[symbol]) for symbol in symbols}


class KellyCriterionSizer(PositionSizer):
    """
    Kelly Criterion position sizing.

    Allocates capital based on expected return and variance to maximize
    long-term growth rate.
    """

    def __init__(self, fraction: float = 1.0):
        """
        Initialize Kelly criterion sizer.

        Args:
            fraction: Fraction of Kelly to use (0.5 = half Kelly, safer)
        """
        self.fraction = fraction

    def calculate_weights(
        self,
        symbols: list[str],
        prices: Dict[str, float],
        capital: float,
        returns: Optional[pd.DataFrame] = None,
        **kwargs
    ) -> Dict[str, float]:
        """
        Calculate Kelly criterion weights.

        Args:
            symbols: List of symbols
            prices: Current prices
            capital: Total capital
            returns: Historical returns DataFrame (required)

        Returns:
            Kelly criterion weights (normalized)

        Raises:
            ValueError: If returns data is not provided
        """
        if returns is None or returns.empty:
            raise ValueError("Kelly criterion sizing requires returns data")

        # Calculate expected returns and variances
        expected_returns = returns[symbols].mean()
        variances = returns[symbols].var()

        # Kelly formula: f = mu / sigma^2
        # Avoid division by zero
        kelly_fractions = np.where(
            variances > 0,
            expected_returns / variances,
            0.0
        )

        # Apply fraction (e.g., half Kelly)
        kelly_fractions = kelly_fractions * self.fraction

        # Set negative weights to zero (don't short)
        kelly_fractions = np.maximum(kelly_fractions, 0)

        # Normalize to sum to 1
        total = kelly_fractions.sum()
        if total > 0:
            weights_array = kelly_fractions / total
        else:
            # If all weights are zero, use equal weight
            weights_array = np.ones(len(symbols)) / len(symbols)

        return {symbol: float(weights_array[i]) for i, symbol in enumerate(symbols)}


class Rebalancer(ABC):
    """
    Abstract base class for portfolio rebalancing logic.

    Rebalancers determine when the portfolio should be rebalanced to target weights.
    """

    @abstractmethod
    def should_rebalance(
        self,
        current_time: pd.Timestamp,
        last_rebalance: Optional[pd.Timestamp] = None,
        **kwargs
    ) -> bool:
        """
        Determine if portfolio should be rebalanced.

        Args:
            current_time: Current timestamp
            last_rebalance: Timestamp of last rebalance (None if first time)
            **kwargs: Additional parameters

        Returns:
            True if should rebalance, False otherwise
        """
        pass


class PeriodicRebalancer(Rebalancer):
    """
    Periodic rebalancing strategy.

    Rebalances the portfolio at fixed time intervals (e.g., monthly, quarterly).
    """

    def __init__(self, frequency_days: int):
        """
        Initialize periodic rebalancer.

        Args:
            frequency_days: Number of days between rebalances
        """
        self.frequency_days = frequency_days

    def should_rebalance(
        self,
        current_time: pd.Timestamp,
        last_rebalance: Optional[pd.Timestamp] = None,
        **kwargs
    ) -> bool:
        """
        Check if enough time has passed since last rebalance.

        Args:
            current_time: Current timestamp
            last_rebalance: Timestamp of last rebalance

        Returns:
            True if should rebalance
        """
        if last_rebalance is None:
            return True

        days_since = (current_time - last_rebalance).days
        return days_since >= self.frequency_days


class ThresholdRebalancer(Rebalancer):
    """
    Threshold-based rebalancing strategy.

    Rebalances when any position weight deviates from target by more than threshold.
    """

    def __init__(self, threshold: float):
        """
        Initialize threshold rebalancer.

        Args:
            threshold: Maximum deviation from target weight (e.g., 0.05 for 5%)
        """
        self.threshold = threshold

    def should_rebalance(
        self,
        current_time: pd.Timestamp,
        last_rebalance: Optional[pd.Timestamp] = None,
        current_weights: Optional[Dict[str, float]] = None,
        target_weights: Optional[Dict[str, float]] = None,
        **kwargs
    ) -> bool:
        """
        Check if any weight has deviated beyond threshold.

        Args:
            current_time: Current timestamp
            last_rebalance: Timestamp of last rebalance
            current_weights: Current portfolio weights
            target_weights: Target portfolio weights

        Returns:
            True if should rebalance
        """
        if current_weights is None or target_weights is None:
            return True

        # Check if any weight deviates beyond threshold
        for symbol in target_weights:
            if symbol in current_weights:
                deviation = abs(current_weights[symbol] - target_weights[symbol])
                if deviation > self.threshold:
                    return True

        return False
