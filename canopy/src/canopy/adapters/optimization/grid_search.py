"""
Grid Search Optimizer Adapter.

Implements exhaustive grid search over parameter space.
Supports parallel execution using multiprocessing.
"""

import time
import itertools
from typing import List, Dict, Any, Callable
from multiprocessing import Pool, cpu_count
from canopy.ports.optimizer import IOptimizer
from canopy.domain.optimization import (
    ParameterSpace,
    ObjectiveFunction,
    OptimizationResult,
)


def _evaluate_parameters(args):
    """
    Helper function for parallel evaluation.

    Args:
        args: Tuple of (objective_function, parameters)

    Returns:
        Tuple of (parameters, objective_value)
    """
    objective_func, params = args
    try:
        value = objective_func(params)
        return params, value
    except Exception as e:
        # Return negative infinity for failed evaluations
        return params, float('-inf')


class GridSearchOptimizer(IOptimizer):
    """
    Grid Search optimizer adapter.

    Exhaustively searches all combinations of parameters.
    Supports parallel execution for faster optimization.
    """

    def __init__(self, n_jobs: int = 1):
        """
        Initialize grid search optimizer.

        Args:
            n_jobs: Number of parallel jobs (1 = sequential, -1 = all CPUs)
        """
        self.n_jobs = n_jobs if n_jobs > 0 else cpu_count()

    def optimize(
        self,
        objective_function: Callable[[Dict[str, Any]], float],
        parameter_spaces: List[ParameterSpace],
        objective: ObjectiveFunction,
    ) -> OptimizationResult:
        """
        Optimize using grid search.

        Args:
            objective_function: Function to optimize
            parameter_spaces: List of parameter spaces
            objective: Objective configuration

        Returns:
            OptimizationResult with optimal parameters
        """
        start_time = time.time()

        # Generate all parameter combinations
        param_grids = {
            ps.name: ps.get_grid_values()
            for ps in parameter_spaces
        }

        param_names = list(param_grids.keys())
        param_values_list = list(param_grids.values())

        # Create all combinations
        all_combinations = list(itertools.product(*param_values_list))

        # Convert to list of parameter dictionaries
        param_dicts = [
            dict(zip(param_names, combo))
            for combo in all_combinations
        ]

        # Evaluate all combinations
        if self.n_jobs == 1:
            # Sequential evaluation
            results = []
            for params in param_dicts:
                value = objective_function(params)
                results.append((params, value))
        else:
            # Parallel evaluation
            with Pool(processes=self.n_jobs) as pool:
                eval_args = [(objective_function, params) for params in param_dicts]
                results = pool.map(_evaluate_parameters, eval_args)

        # Find best result
        best_params = None
        best_value = float('-inf') if objective.maximize else float('inf')
        convergence_history = []

        for params, value in results:
            # Track best so far for convergence history
            if objective.maximize:
                is_better = value > best_value
            else:
                is_better = abs(value) < abs(best_value)

            if is_better:
                best_value = value
                best_params = params

            convergence_history.append(best_value)

        optimization_time = time.time() - start_time

        return OptimizationResult(
            parameters=best_params if best_params else {},
            objective_value=best_value,
            metrics={objective.metric_name: best_value},
            backtest_count=len(param_dicts),
            optimization_time=optimization_time,
            maximize=objective.maximize,
            convergence_history=convergence_history
        )

    def supports_parallel(self) -> bool:
        """Grid search supports parallel execution"""
        return True

    def supports_early_stopping(self) -> bool:
        """Grid search does not support early stopping"""
        return False
