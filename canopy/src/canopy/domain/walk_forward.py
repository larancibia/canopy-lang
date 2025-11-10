"""
Walk-forward analysis domain models.

Walk-forward analysis is a robust validation technique that tests
strategies on out-of-sample data to detect overfitting.
"""

from enum import Enum
from typing import List, Dict, Any
from pydantic import BaseModel, field_validator


class WindowMode(str, Enum):
    """Window mode for walk-forward analysis"""
    ROLLING = "rolling"  # Fixed-size window that slides forward
    ANCHORED = "anchored"  # Growing window anchored at start


class WalkForwardConfig(BaseModel):
    """
    Configuration for walk-forward analysis.

    Defines how to split data into training and testing windows.
    """

    train_size: int
    test_size: int
    mode: WindowMode = WindowMode.ROLLING

    @field_validator('train_size')
    @classmethod
    def validate_train_size(cls, v: int) -> int:
        """Validate that train_size is positive"""
        if v <= 0:
            raise ValueError("train_size must be positive")
        return v

    @field_validator('test_size')
    @classmethod
    def validate_test_size(cls, v: int) -> int:
        """Validate that test_size is positive"""
        if v <= 0:
            raise ValueError("test_size must be positive")
        return v


class WalkForwardWindow(BaseModel):
    """
    Represents a single walk-forward window.

    Each window contains training and testing periods for
    optimization and validation.
    """

    window_id: int
    train_start: int
    train_end: int
    test_start: int
    test_end: int
    train_metrics: Dict[str, float] = {}
    test_metrics: Dict[str, float] = {}
    parameters: Dict[str, Any] = {}

    def train_size(self) -> int:
        """Calculate training window size"""
        return self.train_end - self.train_start

    def test_size(self) -> int:
        """Calculate testing window size"""
        return self.test_end - self.test_start


class WalkForwardResult(BaseModel):
    """
    Results from walk-forward analysis.

    Contains all windows and aggregate metrics comparing
    in-sample vs out-of-sample performance.
    """

    windows: List[WalkForwardWindow]
    in_sample_metrics: Dict[str, float]
    out_of_sample_metrics: Dict[str, float]
    optimization_parameters: Dict[str, Any]
    total_windows: int

    def is_overfit(self, threshold: float = 0.3) -> bool:
        """
        Detect if strategy is overfit.

        A strategy is considered overfit if out-of-sample performance
        degrades significantly compared to in-sample performance.

        Args:
            threshold: Maximum acceptable performance degradation (default 30%)

        Returns:
            True if strategy appears overfit
        """
        degradation = self.performance_degradation()
        return degradation > threshold

    def performance_degradation(self, metric: str = "sharpe_ratio") -> float:
        """
        Calculate performance degradation from in-sample to out-of-sample.

        Args:
            metric: Metric to compare (default "sharpe_ratio")

        Returns:
            Degradation as a fraction (e.g., 0.25 = 25% degradation)
        """
        in_sample = self.in_sample_metrics.get(metric, 0.0)
        out_of_sample = self.out_of_sample_metrics.get(metric, 0.0)

        if in_sample == 0.0:
            return 0.0

        degradation = (in_sample - out_of_sample) / abs(in_sample)
        return max(0.0, degradation)  # Only count degradation, not improvement

    def average_sharpe_ratio(self) -> float:
        """
        Calculate average Sharpe ratio across in-sample and out-of-sample.

        Returns:
            Average Sharpe ratio
        """
        in_sample = self.in_sample_metrics.get("sharpe_ratio", 0.0)
        out_of_sample = self.out_of_sample_metrics.get("sharpe_ratio", 0.0)
        return (in_sample + out_of_sample) / 2.0
