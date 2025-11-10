"""
Bayesian Optimizer Adapter.

Implements Bayesian optimization using scikit-optimize (skopt).
Uses Gaussian processes to efficiently explore parameter space.
"""

import time
from typing import List, Dict, Any, Callable, Optional
import numpy as np
from skopt import gp_minimize
from skopt.space import Real, Integer
from canopy.ports.optimizer import IOptimizer
from canopy.domain.optimization import (
    ParameterSpace,
    ObjectiveFunction,
    OptimizationResult,
)


class BayesianOptimizer(IOptimizer):
    """
    Bayesian Optimizer adapter.

    Uses Gaussian processes to model the objective function
    and intelligently explore the parameter space.
    More efficient than grid search for expensive evaluations.
    """

    def __init__(
        self,
        n_iterations: int = 50,
        n_initial_points: int = 10,
        acquisition_func: str = "EI",  # Expected Improvement
        random_seed: Optional[int] = None
    ):
        """
        Initialize Bayesian optimizer.

        Args:
            n_iterations: Total number of evaluations
            n_initial_points: Number of random initial points
            acquisition_func: Acquisition function ("EI", "PI", "LCB")
            random_seed: Random seed for reproducibility
        """
        self.n_iterations = n_iterations
        self.n_initial_points = n_initial_points
        self.acquisition_func = acquisition_func
        self.random_seed = random_seed

    def optimize(
        self,
        objective_function: Callable[[Dict[str, Any]], float],
        parameter_spaces: List[ParameterSpace],
        objective: ObjectiveFunction,
    ) -> OptimizationResult:
        """
        Optimize using Bayesian optimization.

        Args:
            objective_function: Function to optimize
            parameter_spaces: List of parameter spaces
            objective: Objective configuration

        Returns:
            OptimizationResult with optimal parameters
        """
        start_time = time.time()

        # Convert parameter spaces to skopt format
        dimensions = []
        param_names = []

        for ps in parameter_spaces:
            param_names.append(ps.name)
            if ps.type == "integer":
                dimensions.append(Integer(
                    int(ps.min_value),
                    int(ps.max_value),
                    name=ps.name
                ))
            else:
                dimensions.append(Real(
                    ps.min_value,
                    ps.max_value,
                    name=ps.name
                ))

        # Wrapper to convert from list to dict
        evaluations = []
        convergence_history = []
        best_value = float('-inf') if objective.maximize else float('inf')

        def objective_wrapper(x):
            params = {name: val for name, val in zip(param_names, x)}
            value = objective_function(params)

            # Track convergence
            nonlocal best_value
            if objective.maximize:
                if value > best_value:
                    best_value = value
            else:
                if abs(value) < abs(best_value):
                    best_value = value

            convergence_history.append(best_value)
            evaluations.append((params, value))

            # skopt minimizes by default, so negate if maximizing
            return -value if objective.maximize else value

        # Run Bayesian optimization
        result = gp_minimize(
            objective_wrapper,
            dimensions,
            n_calls=self.n_iterations,
            n_initial_points=self.n_initial_points,
            acq_func=self.acquisition_func,
            random_state=self.random_seed,
            verbose=False
        )

        # Extract best parameters
        best_x = result.x
        best_params = {name: val for name, val in zip(param_names, best_x)}

        # Get best value (un-negate if we were maximizing)
        best_objective_value = -result.fun if objective.maximize else result.fun

        optimization_time = time.time() - start_time

        return OptimizationResult(
            parameters=best_params,
            objective_value=best_objective_value,
            metrics={objective.metric_name: best_objective_value},
            backtest_count=len(evaluations),
            optimization_time=optimization_time,
            maximize=objective.maximize,
            convergence_history=convergence_history
        )

    def supports_parallel(self) -> bool:
        """Bayesian optimization doesn't support parallel by default"""
        return False

    def supports_early_stopping(self) -> bool:
        """Bayesian optimization supports early stopping"""
        return True
