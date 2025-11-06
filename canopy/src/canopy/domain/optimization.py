"""
Optimization domain models - Pure business logic for strategy optimization.

This module contains the core domain models for parameter optimization,
following hexagonal architecture principles.
"""

from enum import Enum
from typing import Dict, Any, List
import numpy as np
from pydantic import BaseModel, field_validator


class ParameterType(str, Enum):
    """Type of optimization parameter"""
    INTEGER = "integer"
    FLOAT = "float"


class ParameterSpace(BaseModel):
    """
    Defines the search space for a single parameter.

    A parameter space specifies the range and type of values that
    a strategy parameter can take during optimization.
    """

    name: str
    type: ParameterType
    min_value: float
    max_value: float
    step: float = 1.0

    @field_validator('max_value')
    @classmethod
    def validate_range(cls, v: float, info) -> float:
        """Validate that min_value <= max_value"""
        if 'min_value' in info.data and v < info.data['min_value']:
            raise ValueError("min_value must be less than or equal to max_value")
        return v

    def get_grid_values(self) -> List[Any]:
        """
        Generate grid of values for grid search.

        Returns:
            List of values spanning the parameter space
        """
        values = np.arange(self.min_value, self.max_value + self.step/2, self.step)

        if self.type == ParameterType.INTEGER:
            return [int(v) for v in values]
        else:
            return [float(v) for v in values]

    def sample_random_value(self) -> Any:
        """
        Sample a random value from the parameter space.

        Returns:
            Random value within the parameter range
        """
        if self.type == ParameterType.INTEGER:
            return int(np.random.randint(int(self.min_value), int(self.max_value) + 1))
        else:
            return float(np.random.uniform(self.min_value, self.max_value))


class ObjectiveFunction(BaseModel):
    """
    Defines what metric to optimize.

    The objective function determines which performance metric
    the optimization algorithm should maximize or minimize.
    """

    name: str
    maximize: bool = True
    metric_name: str = ""

    def __init__(self, **data):
        super().__init__(**data)
        # If metric_name not provided, use name as metric_name
        if not self.metric_name:
            object.__setattr__(self, 'metric_name', self.name)

    @staticmethod
    def sharpe_ratio() -> "ObjectiveFunction":
        """Create objective to maximize Sharpe ratio"""
        return ObjectiveFunction(
            name="sharpe_ratio",
            maximize=True,
            metric_name="sharpe_ratio"
        )

    @staticmethod
    def total_return() -> "ObjectiveFunction":
        """Create objective to maximize total return"""
        return ObjectiveFunction(
            name="total_return",
            maximize=True,
            metric_name="total_return"
        )

    @staticmethod
    def max_drawdown() -> "ObjectiveFunction":
        """Create objective to minimize max drawdown (minimize negative values)"""
        return ObjectiveFunction(
            name="max_drawdown",
            maximize=False,
            metric_name="max_drawdown"
        )

    @staticmethod
    def sortino_ratio() -> "ObjectiveFunction":
        """Create objective to maximize Sortino ratio"""
        return ObjectiveFunction(
            name="sortino_ratio",
            maximize=True,
            metric_name="sortino_ratio"
        )

    @staticmethod
    def calmar_ratio() -> "ObjectiveFunction":
        """Create objective to maximize Calmar ratio"""
        return ObjectiveFunction(
            name="calmar_ratio",
            maximize=True,
            metric_name="calmar_ratio"
        )


class OptimizationResult(BaseModel):
    """
    Stores the results of an optimization run.

    Contains the optimal parameters found, objective value achieved,
    and metadata about the optimization process.
    """

    parameters: Dict[str, Any]
    objective_value: float
    metrics: Dict[str, float]
    backtest_count: int
    optimization_time: float
    maximize: bool = True
    convergence_history: List[float] = []

    def is_better_than(self, other: "OptimizationResult") -> bool:
        """
        Compare two optimization results.

        Args:
            other: Another OptimizationResult to compare against

        Returns:
            True if this result is better than the other
        """
        if self.maximize:
            return self.objective_value > other.objective_value
        else:
            # When minimizing, smaller absolute value is better
            # This handles both positive values (minimize error: 5 < 10)
            # and negative values (minimize drawdown: -10 better than -15)
            return abs(self.objective_value) < abs(other.objective_value)
