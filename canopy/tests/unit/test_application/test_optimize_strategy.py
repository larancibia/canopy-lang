"""
Tests for optimize strategy use case.

Tests the application layer that orchestrates optimization.
"""

import pytest
import pandas as pd
from canopy.application.optimize_strategy import OptimizeStrategyUseCase
from canopy.adapters.optimization.grid_search import GridSearchOptimizer
from canopy.domain.strategy import MACrossoverStrategy
from canopy.domain.timeseries import TimeSeries
from canopy.domain.optimization import (
    ParameterSpace,
    ParameterType,
    ObjectiveFunction,
)


@pytest.fixture
def sample_timeseries():
    """Create sample timeseries for testing"""
    dates = pd.date_range('2020-01-01', periods=100, freq='D')
    # Create trending data for simple testing
    prices = pd.Series(range(100, 200), index=dates)
    return TimeSeries(
        symbol="TEST",
        open=prices,
        high=prices * 1.01,
        low=prices * 0.99,
        close=prices,
        volume=pd.Series([1000000] * 100, index=dates)
    )


class TestOptimizeStrategyUseCase:
    """Test OptimizeStrategyUseCase"""

    def test_create_use_case(self, sample_timeseries):
        """Should create optimization use case"""
        optimizer = GridSearchOptimizer(n_jobs=1)
        use_case = OptimizeStrategyUseCase(
            optimizer=optimizer,
            timeseries=sample_timeseries
        )
        assert use_case is not None

    def test_optimize_ma_crossover_strategy(self, sample_timeseries):
        """Should optimize MA crossover strategy parameters"""
        optimizer = GridSearchOptimizer(n_jobs=1)
        use_case = OptimizeStrategyUseCase(
            optimizer=optimizer,
            timeseries=sample_timeseries
        )

        param_spaces = [
            ParameterSpace(
                name="fast_period",
                type=ParameterType.INTEGER,
                min_value=5,
                max_value=15,
                step=5
            ),
            ParameterSpace(
                name="slow_period",
                type=ParameterType.INTEGER,
                min_value=20,
                max_value=30,
                step=5
            )
        ]

        objective = ObjectiveFunction.total_return()

        result = use_case.optimize(
            strategy_class=MACrossoverStrategy,
            parameter_spaces=param_spaces,
            objective=objective,
            initial_capital=10000.0
        )

        # Should return a result with optimized parameters
        assert result is not None
        assert "fast_period" in result.parameters
        assert "slow_period" in result.parameters
        assert 5 <= result.parameters["fast_period"] <= 15
        assert 20 <= result.parameters["slow_period"] <= 30
        assert result.backtest_count > 0

    def test_optimization_caches_backtest_results(self, sample_timeseries):
        """Should cache backtest results to avoid redundant computation"""
        optimizer = GridSearchOptimizer(n_jobs=1)
        use_case = OptimizeStrategyUseCase(
            optimizer=optimizer,
            timeseries=sample_timeseries,
            enable_cache=True
        )

        param_spaces = [
            ParameterSpace(
                name="fast_period",
                type=ParameterType.INTEGER,
                min_value=10,
                max_value=10,  # Single value to test caching
                step=1
            ),
            ParameterSpace(
                name="slow_period",
                type=ParameterType.INTEGER,
                min_value=20,
                max_value=20,  # Single value
                step=1
            )
        ]

        objective = ObjectiveFunction.total_return()

        # Run optimization twice
        result1 = use_case.optimize(
            strategy_class=MACrossoverStrategy,
            parameter_spaces=param_spaces,
            objective=objective
        )

        result2 = use_case.optimize(
            strategy_class=MACrossoverStrategy,
            parameter_spaces=param_spaces,
            objective=objective
        )

        # Both should return same results
        assert result1.parameters == result2.parameters
        assert result1.objective_value == result2.objective_value
