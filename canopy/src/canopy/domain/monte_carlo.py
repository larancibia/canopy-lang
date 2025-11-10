"""
Monte Carlo simulation domain models.

Monte Carlo simulation randomizes trade sequences to estimate
confidence intervals, worst-case scenarios, and risk metrics.
"""

from typing import List, Optional
import numpy as np
from pydantic import BaseModel, field_validator


class MonteCarloConfig(BaseModel):
    """
    Configuration for Monte Carlo simulation.

    Defines the number of simulations and confidence levels.
    """

    n_simulations: int
    confidence_level: float = 0.95
    random_seed: Optional[int] = None

    @field_validator('n_simulations')
    @classmethod
    def validate_n_simulations(cls, v: int) -> int:
        """Validate that n_simulations is positive"""
        if v <= 0:
            raise ValueError("n_simulations must be positive")
        return v

    @field_validator('confidence_level')
    @classmethod
    def validate_confidence_level(cls, v: float) -> float:
        """Validate that confidence_level is between 0 and 1"""
        if not 0 < v < 1:
            raise ValueError("confidence_level must be between 0 and 1")
        return v


class ConfidenceInterval(BaseModel):
    """
    Confidence interval for a metric.

    Represents the range of values with a specified confidence level.
    """

    lower: float
    upper: float
    median: float
    confidence_level: float

    def range(self) -> float:
        """
        Calculate the range of the confidence interval.

        Returns:
            Range (upper - lower)
        """
        return self.upper - self.lower


class MonteCarloResult(BaseModel):
    """
    Results from Monte Carlo simulation.

    Contains simulated returns and statistical metrics including
    confidence intervals and risk measures.
    """

    simulated_returns: List[float]
    confidence_interval: ConfidenceInterval
    worst_case_return: float
    best_case_return: float
    expected_return: float
    risk_of_ruin: float
    n_simulations: int

    def percentile(self, p: float) -> float:
        """
        Calculate percentile of simulated returns.

        Args:
            p: Percentile to calculate (0.0 to 1.0)

        Returns:
            Value at the specified percentile
        """
        return float(np.percentile(self.simulated_returns, p * 100))

    def probability_of_loss(self) -> float:
        """
        Calculate probability of loss (negative return).

        Returns:
            Probability as a fraction (0.0 to 1.0)
        """
        losses = sum(1 for r in self.simulated_returns if r < 0)
        return losses / len(self.simulated_returns)

    def mean(self) -> float:
        """
        Calculate mean of simulated returns.

        Returns:
            Mean return
        """
        return float(np.mean(self.simulated_returns))

    def std(self) -> float:
        """
        Calculate standard deviation of simulated returns.

        Returns:
            Standard deviation
        """
        return float(np.std(self.simulated_returns))

    def var(self, confidence_level: float = 0.95) -> float:
        """
        Calculate Value at Risk (VaR).

        VaR represents the maximum loss at a given confidence level.

        Args:
            confidence_level: Confidence level (default 0.95)

        Returns:
            VaR value (positive number representing loss)
        """
        alpha = 1 - confidence_level
        var_value = self.percentile(alpha)
        return float(-var_value) if var_value < 0 else 0.0

    def cvar(self, confidence_level: float = 0.95) -> float:
        """
        Calculate Conditional Value at Risk (CVaR).

        CVaR is the expected loss given that we're in the tail
        beyond VaR (also called Expected Shortfall).

        Args:
            confidence_level: Confidence level (default 0.95)

        Returns:
            CVaR value (positive number representing expected loss)
        """
        alpha = 1 - confidence_level
        var_threshold = self.percentile(alpha)
        tail_losses = [r for r in self.simulated_returns if r <= var_threshold]

        if not tail_losses:
            return 0.0

        mean_tail_loss = np.mean(tail_losses)
        return float(-mean_tail_loss) if mean_tail_loss < 0 else 0.0
