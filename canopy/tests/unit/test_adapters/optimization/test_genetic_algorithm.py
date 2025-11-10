"""
Tests for genetic algorithm optimizer adapter.

Genetic algorithms use evolutionary principles for optimization.
"""

import pytest
from canopy.adapters.optimization.genetic_algorithm import GeneticAlgorithmOptimizer
from canopy.domain.optimization import (
    ParameterSpace,
    ParameterType,
    ObjectiveFunction,
)


class TestGeneticAlgorithmOptimizer:
    """Test GeneticAlgorithmOptimizer adapter"""

    def test_create_optimizer(self):
        """Should create genetic algorithm optimizer"""
        optimizer = GeneticAlgorithmOptimizer(
            population_size=20,
            n_generations=10
        )
        assert optimizer is not None
        assert optimizer.population_size == 20
        assert optimizer.n_generations == 10

    def test_default_parameters(self):
        """Should use default parameters"""
        optimizer = GeneticAlgorithmOptimizer()
        assert optimizer.population_size == 50
        assert optimizer.n_generations == 100
        assert optimizer.crossover_prob == 0.8
        assert optimizer.mutation_prob == 0.2

    def test_supports_parallel(self):
        """Should support parallel execution"""
        optimizer = GeneticAlgorithmOptimizer()
        assert optimizer.supports_parallel() is True

    def test_supports_early_stopping(self):
        """Should support early stopping"""
        optimizer = GeneticAlgorithmOptimizer()
        assert optimizer.supports_early_stopping() is True

    def test_optimize_single_parameter(self):
        """Should optimize single parameter using evolution"""
        optimizer = GeneticAlgorithmOptimizer(
            population_size=20,
            n_generations=50,
            random_seed=42
        )

        # Simple function: f(x) = -(x-7)^2 + 15
        # Maximum at x=7
        def objective_func(params):
            x = params["x"]
            return -(x - 7) ** 2 + 15

        param_space = ParameterSpace(
            name="x",
            type=ParameterType.INTEGER,
            min_value=0,
            max_value=15,
            step=1
        )

        objective = ObjectiveFunction.sharpe_ratio()

        result = optimizer.optimize(
            objective_function=objective_func,
            parameter_spaces=[param_space],
            objective=objective
        )

        # Should find x close to 7
        assert abs(result.parameters["x"] - 7) <= 2  # Within 2 of optimal
        assert result.objective_value >= 10  # Close to maximum of 15
        assert result.backtest_count > 0

    def test_optimize_two_parameters(self):
        """Should optimize two parameters"""
        optimizer = GeneticAlgorithmOptimizer(
            population_size=30,
            n_generations=50,
            random_seed=42
        )

        # Sphere function: f(x,y) = -(x-5)^2 - (y-10)^2 + 30
        # Maximum at (5, 10)
        def objective_func(params):
            x = params["x"]
            y = params["y"]
            return -(x - 5) ** 2 - (y - 10) ** 2 + 30

        param_spaces = [
            ParameterSpace(
                name="x",
                type=ParameterType.INTEGER,
                min_value=0,
                max_value=10,
                step=1
            ),
            ParameterSpace(
                name="y",
                type=ParameterType.INTEGER,
                min_value=5,
                max_value=15,
                step=1
            )
        ]

        objective = ObjectiveFunction.sharpe_ratio()

        result = optimizer.optimize(
            objective_function=objective_func,
            parameter_spaces=param_spaces,
            objective=objective
        )

        # Should find parameters close to optimal
        assert abs(result.parameters["x"] - 5) <= 2
        assert abs(result.parameters["y"] - 10) <= 2
        assert result.objective_value >= 20  # Close to maximum of 30

    def test_convergence_history(self):
        """Should track convergence over generations"""
        optimizer = GeneticAlgorithmOptimizer(
            population_size=20,
            n_generations=30,
            random_seed=42
        )

        def objective_func(params):
            return -(params["x"] - 5) ** 2 + 10

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

        # Should have convergence history
        assert len(result.convergence_history) > 0
        # Convergence should improve or stay same over time
        # (allowing some fluctuation in early generations)
        assert result.convergence_history[-1] >= result.convergence_history[0] - 5

    def test_early_stopping(self):
        """Should stop early when converged"""
        optimizer = GeneticAlgorithmOptimizer(
            population_size=20,
            n_generations=100,
            early_stopping_rounds=10,
            random_seed=42
        )

        def objective_func(params):
            return -(params["x"] - 5) ** 2 + 10

        param_space = ParameterSpace(
            name="x",
            type=ParameterType.INTEGER,
            min_value=0,
            max_value=10,
            step=1
        )

        objective = ObjectiveFunction.sharpe_ratio()

        result = optimizer.optimize(
            objective_function=objective_func,
            parameter_spaces=[param_space],
            objective=objective
        )

        # Should stop before 100 generations
        # (convergence history tracks generations)
        assert len(result.convergence_history) < 100
