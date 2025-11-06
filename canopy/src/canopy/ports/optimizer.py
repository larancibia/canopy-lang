"""
Optimizer Port - Interface for strategy optimizers.

This module defines the port (interface) for optimizers following
hexagonal architecture. Adapters will implement this interface.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Callable
from canopy.domain.optimization import (
    ParameterSpace,
    ObjectiveFunction,
    OptimizationResult,
)


class IOptimizer(ABC):
    """
    Port for strategy optimizers.

    This interface defines the contract that all optimizer adapters
    must implement. It allows the application to swap different
    optimization algorithms without changing business logic.
    """

    @abstractmethod
    def optimize(
        self,
        objective_function: Callable[[Dict[str, Any]], float],
        parameter_spaces: List[ParameterSpace],
        objective: ObjectiveFunction,
    ) -> OptimizationResult:
        """
        Optimize strategy parameters.

        Args:
            objective_function: Function that takes parameters and returns objective value
            parameter_spaces: List of parameter spaces to optimize
            objective: Objective function configuration (maximize/minimize)

        Returns:
            OptimizationResult with optimal parameters and metrics

        Raises:
            ValueError: If inputs are invalid
        """
        pass

    @abstractmethod
    def supports_parallel(self) -> bool:
        """
        Check if optimizer supports parallel execution.

        Returns:
            True if optimizer can run evaluations in parallel
        """
        pass

    @abstractmethod
    def supports_early_stopping(self) -> bool:
        """
        Check if optimizer supports early stopping.

        Returns:
            True if optimizer can stop early when converged
        """
        pass
