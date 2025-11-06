"""
Robustness testing domain models.

Robustness testing validates strategy stability across parameter changes,
noise injection, and different market regimes.
"""

from enum import Enum
from typing import List, Any
import numpy as np
from pydantic import BaseModel, field_validator


class RegimeType(str, Enum):
    """Market regime types"""
    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"
    CRISIS = "crisis"


class SensitivityTestConfig(BaseModel):
    """
    Configuration for parameter sensitivity testing.

    Tests how strategy performance varies with parameter changes.
    """

    parameter_name: str
    base_value: Any
    perturbation_range: float = 0.1  # ±10% by default
    n_steps: int = 5

    def get_test_values(self) -> List[Any]:
        """
        Generate parameter values to test.

        Returns:
            List of parameter values around base_value
        """
        if isinstance(self.base_value, int):
            # Integer parameter
            delta = max(1, int(self.base_value * self.perturbation_range))
            min_val = self.base_value - delta
            max_val = self.base_value + delta
            step = max(1, (max_val - min_val) // (self.n_steps - 1))
            return list(range(min_val, max_val + 1, step))
        else:
            # Float parameter
            delta = self.base_value * self.perturbation_range
            min_val = self.base_value - delta
            max_val = self.base_value + delta
            return [float(v) for v in np.linspace(min_val, max_val, self.n_steps)]


class SensitivityTestResult(BaseModel):
    """
    Results from parameter sensitivity testing.

    Shows how performance varies across parameter values.
    """

    parameter_name: str
    base_value: Any
    test_values: List[Any]
    metric_values: List[float]
    metric_name: str

    def sensitivity_score(self) -> float:
        """
        Calculate sensitivity score.

        Uses coefficient of variation (std / mean) to measure
        how much performance varies with parameter changes.

        Returns:
            Sensitivity score (lower is more robust)
        """
        if len(self.metric_values) == 0:
            return 0.0

        mean = np.mean(self.metric_values)
        std = np.std(self.metric_values)

        if mean == 0:
            return 0.0

        return float(std / abs(mean))

    def is_robust(self, threshold: float = 0.2) -> bool:
        """
        Determine if parameter is robust.

        A parameter is considered robust if its sensitivity score
        is below the threshold.

        Args:
            threshold: Maximum acceptable sensitivity (default 0.2)

        Returns:
            True if parameter is robust
        """
        return self.sensitivity_score() < threshold

    def best_value(self) -> Any:
        """
        Find parameter value with best performance.

        Returns:
            Parameter value that achieved highest metric
        """
        if not self.metric_values:
            return self.base_value

        best_idx = int(np.argmax(self.metric_values))
        return self.test_values[best_idx]


class NoiseConfig(BaseModel):
    """
    Configuration for noise injection testing.

    Tests strategy robustness by adding noise to price data.
    """

    noise_level: float
    noise_type: str = "gaussian"

    @field_validator('noise_level')
    @classmethod
    def validate_noise_level(cls, v: float) -> float:
        """Validate that noise_level is non-negative"""
        if v < 0:
            raise ValueError("noise_level must be non-negative")
        return v


class NoiseTestResult(BaseModel):
    """
    Results from noise injection testing.

    Shows how strategy performs when price data is perturbed.
    """

    noise_level: float
    original_metric: float
    noisy_metrics: List[float]
    metric_name: str

    def average_noisy_metric(self) -> float:
        """
        Calculate average metric across noisy simulations.

        Returns:
            Average metric value
        """
        if not self.noisy_metrics:
            return 0.0
        return float(np.mean(self.noisy_metrics))

    def performance_degradation(self) -> float:
        """
        Calculate performance degradation due to noise.

        Returns:
            Degradation as a fraction
        """
        avg_noisy = self.average_noisy_metric()
        if self.original_metric == 0:
            return 0.0
        return (self.original_metric - avg_noisy) / abs(self.original_metric)

    def is_robust_to_noise(self, threshold: float = 0.2) -> bool:
        """
        Determine if strategy is robust to noise.

        Args:
            threshold: Maximum acceptable degradation (default 20%)

        Returns:
            True if strategy is robust to noise
        """
        return self.performance_degradation() < threshold


class RegimeAnalysisResult(BaseModel):
    """
    Results from market regime analysis.

    Shows strategy performance across different market conditions.
    """

    regime_metrics: dict[RegimeType, dict[str, float]]
    overall_metrics: dict[str, float]

    def best_regime(self, metric_name: str = "sharpe_ratio") -> RegimeType:
        """
        Find regime where strategy performs best.

        Args:
            metric_name: Metric to compare (default "sharpe_ratio")

        Returns:
            Regime with best performance
        """
        if not self.regime_metrics:
            return RegimeType.SIDEWAYS

        best = max(
            self.regime_metrics.items(),
            key=lambda x: x[1].get(metric_name, 0.0)
        )
        return best[0]

    def worst_regime(self, metric_name: str = "sharpe_ratio") -> RegimeType:
        """
        Find regime where strategy performs worst.

        Args:
            metric_name: Metric to compare (default "sharpe_ratio")

        Returns:
            Regime with worst performance
        """
        if not self.regime_metrics:
            return RegimeType.SIDEWAYS

        worst = min(
            self.regime_metrics.items(),
            key=lambda x: x[1].get(metric_name, 0.0)
        )
        return worst[0]

    def regime_consistency(self, metric_name: str = "sharpe_ratio") -> float:
        """
        Calculate consistency across regimes.

        Measures coefficient of variation of metric across regimes.

        Args:
            metric_name: Metric to analyze (default "sharpe_ratio")

        Returns:
            Consistency score (lower is more consistent)
        """
        if not self.regime_metrics:
            return 0.0

        values = [
            metrics.get(metric_name, 0.0)
            for metrics in self.regime_metrics.values()
        ]

        mean = np.mean(values)
        std = np.std(values)

        if mean == 0:
            return 0.0

        return float(std / abs(mean))
