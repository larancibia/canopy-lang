"""
Tests for grid search optimizer adapter.

Grid search exhaustively tests all parameter combinations.
"""

import pytest
from canopy.adapters.optimization.grid_search import GridSearchOptimizer
from canopy.domain.optimization import (
    ParameterSpace,
    ParameterType,
    ObjectiveFunction,
)


class TestGridSearchOptimizer:
    """Test GridSearchOptimizer adapter"""

    def test_create_optimizer(self):
        """Should create grid search optimizer"""
        optimizer = GridSearchOptimizer(n_jobs=1)
        assert optimizer is not None
        assert optimizer.n_jobs == 1

    def test_supports_parallel(self):
        """Should support parallel execution"""
        optimizer = GridSearchOptimizer(n_jobs=2)
        assert optimizer.supports_parallel() is True

    def test_does_not_support_early_stopping(self):
        """Grid search does not support early stopping"""
        optimizer = GridSearchOptimizer()
        assert optimizer.supports_early_stopping() is False

    def test_optimize_single_parameter(self):
        """Should optimize single parameter"""
        optimizer = GridSearchOptimizer(n_jobs=1)

        # Simple quadratic function: f(x) = -(x-5)^2 + 10
        # Maximum at x=5 with value 10
        def objective_func(params):
            x = params["x"]
            return -(x - 5) ** 2 + 10

        param_space = ParameterSpace(
            name="x",
            type=ParameterType.INTEGER,
            min_value=0,
            max_value=10,
            step=1
        )

        objective = ObjectiveFunction.total_return()

        result = optimizer.optimize(
            objective_function=objective_func,
            parameter_spaces=[param_space],
            objective=objective
        )

        # Should find x=5 as optimal
        assert result.parameters["x"] == 5
        assert result.objective_value == pytest.approx(10.0)
        assert result.backtest_count == 11  # 0 to 10 inclusive

    def test_optimize_two_parameters(self):
        """Should optimize two parameters"""
        optimizer = GridSearchOptimizer(n_jobs=1)

        # Function: f(x,y) = -(x-3)^2 - (y-7)^2 + 20
        # Maximum at (3, 7) with value 20
        def objective_func(params):
            x = params["x"]
            y = params["y"]
            return -(x - 3) ** 2 - (y - 7) ** 2 + 20

        param_spaces = [
            ParameterSpace(
                name="x",
                type=ParameterType.INTEGER,
                min_value=0,
                max_value=6,
                step=1
            ),
            ParameterSpace(
                name="y",
                type=ParameterType.INTEGER,
                min_value=5,
                max_value=9,
                step=1
            )
        ]

        objective = ObjectiveFunction.total_return()

        result = optimizer.optimize(
            objective_function=objective_func,
            parameter_spaces=param_spaces,
            objective=objective
        )

        # Should find (3, 7) as optimal
        assert result.parameters["x"] == 3
        assert result.parameters["y"] == 7
        assert result.objective_value == pytest.approx(20.0)
        assert result.backtest_count == 7 * 5  # 7 x values * 5 y values

    def test_minimize_objective(self):
        """Should minimize objective when maximize=False"""
        optimizer = GridSearchOptimizer(n_jobs=1)

        # Function: f(x) = (x-5)^2
        # Minimum at x=5 with value 0
        def objective_func(params):
            x = params["x"]
            return (x - 5) ** 2

        param_space = ParameterSpace(
            name="x",
            type=ParameterType.INTEGER,
            min_value=0,
            max_value=10,
            step=1
        )

        objective = ObjectiveFunction.max_drawdown()  # minimize

        result = optimizer.optimize(
            objective_function=objective_func,
            parameter_spaces=[param_space],
            objective=objective
        )

        # Should find x=5 as optimal (minimum)
        assert result.parameters["x"] == 5
        assert result.objective_value == pytest.approx(0.0)

    def test_convergence_history(self):
        """Should track convergence history"""
        optimizer = GridSearchOptimizer(n_jobs=1)

        def objective_func(params):
            return params["x"] * 2

        param_space = ParameterSpace(
            name="x",
            type=ParameterType.INTEGER,
            min_value=1,
            max_value=5,
            step=1
        )

        objective = ObjectiveFunction.total_return()

        result = optimizer.optimize(
            objective_function=objective_func,
            parameter_spaces=[param_space],
            objective=objective
        )

        # Should have convergence history
        assert len(result.convergence_history) == 5
        # Best value should improve or stay same
        for i in range(1, len(result.convergence_history)):
            assert result.convergence_history[i] >= result.convergence_history[i-1]
