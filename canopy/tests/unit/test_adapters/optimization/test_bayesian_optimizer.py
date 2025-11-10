"""
Tests for Bayesian optimizer adapter.

Bayesian optimization uses Gaussian processes for efficient search.
"""

import pytest
from canopy.adapters.optimization.bayesian_optimizer import BayesianOptimizer
from canopy.domain.optimization import (
    ParameterSpace,
    ParameterType,
    ObjectiveFunction,
)


class TestBayesianOptimizer:
    """Test BayesianOptimizer adapter"""

    def test_create_optimizer(self):
        """Should create Bayesian optimizer"""
        optimizer = BayesianOptimizer(n_iterations=20)
        assert optimizer is not None
        assert optimizer.n_iterations == 20

    def test_default_parameters(self):
        """Should use default parameters"""
        optimizer = BayesianOptimizer()
        assert optimizer.n_iterations == 50
        assert optimizer.n_initial_points == 10

    def test_supports_parallel(self):
        """Should not support parallel execution (for now)"""
        optimizer = BayesianOptimizer()
        assert optimizer.supports_parallel() is False

    def test_supports_early_stopping(self):
        """Should support early stopping"""
        optimizer = BayesianOptimizer()
        assert optimizer.supports_early_stopping() is True

    def test_optimize_single_parameter(self):
        """Should optimize single parameter efficiently"""
        optimizer = BayesianOptimizer(
            n_iterations=30,
            n_initial_points=5,
            random_seed=42
        )

        # Simple function: f(x) = -(x-8)^2 + 20
        # Maximum at x=8
        def objective_func(params):
            x = params["x"]
            return -(x - 8) ** 2 + 20

        param_space = ParameterSpace(
            name="x",
            type=ParameterType.FLOAT,
            min_value=0.0,
            max_value=15.0,
            step=0.1
        )

        objective = ObjectiveFunction.sharpe_ratio()

        result = optimizer.optimize(
            objective_function=objective_func,
            parameter_spaces=[param_space],
            objective=objective
        )

        # Should find x close to 8
        assert abs(result.parameters["x"] - 8.0) <= 1.0
        assert result.objective_value >= 15  # Close to maximum of 20
        assert result.backtest_count == 30  # n_iterations

    def test_optimize_two_parameters(self):
        """Should optimize two parameters"""
        optimizer = BayesianOptimizer(
            n_iterations=40,
            n_initial_points=10,
            random_seed=42
        )

        # Function: f(x,y) = -(x-3)^2 - (y-7)^2 + 25
        # Maximum at (3, 7)
        def objective_func(params):
            x = params["x"]
            y = params["y"]
            return -(x - 3) ** 2 - (y - 7) ** 2 + 25

        param_spaces = [
            ParameterSpace(
                name="x",
                type=ParameterType.FLOAT,
                min_value=0.0,
                max_value=6.0,
                step=0.1
            ),
            ParameterSpace(
                name="y",
                type=ParameterType.FLOAT,
                min_value=4.0,
                max_value=10.0,
                step=0.1
            )
        ]

        objective = ObjectiveFunction.sharpe_ratio()

        result = optimizer.optimize(
            objective_function=objective_func,
            parameter_spaces=param_spaces,
            objective=objective
        )

        # Should find parameters close to optimal
        assert abs(result.parameters["x"] - 3.0) <= 1.5
        assert abs(result.parameters["y"] - 7.0) <= 1.5
        assert result.objective_value >= 18  # Close to maximum of 25

    def test_convergence_history(self):
        """Should track convergence over iterations"""
        optimizer = BayesianOptimizer(
            n_iterations=20,
            n_initial_points=5,
            random_seed=42
        )

        def objective_func(params):
            return -(params["x"] - 5) ** 2 + 10

        param_space = ParameterSpace(
            name="x",
            type=ParameterType.FLOAT,
            min_value=0.0,
            max_value=10.0,
            step=0.1
        )

        objective = ObjectiveFunction.total_return()

        result = optimizer.optimize(
            objective_function=objective_func,
            parameter_spaces=[param_space],
            objective=objective
        )

        # Should have convergence history
        assert len(result.convergence_history) == 20
        # Convergence should generally improve
        assert result.convergence_history[-1] >= result.convergence_history[0] - 2
