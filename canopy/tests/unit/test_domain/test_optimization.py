"""
Tests for optimization domain models.

Following TDD principles - these tests define the expected behavior
of our optimization framework before implementation.
"""

import pytest
from canopy.domain.optimization import (
    ParameterSpace,
    ParameterType,
    ObjectiveFunction,
    OptimizationResult,
)


class TestParameterSpace:
    """Test ParameterSpace domain model"""

    def test_create_integer_parameter(self):
        """Should create integer parameter with valid range"""
        param = ParameterSpace(
            name="fast_period",
            type=ParameterType.INTEGER,
            min_value=5,
            max_value=50,
            step=1
        )
        assert param.name == "fast_period"
        assert param.type == ParameterType.INTEGER
        assert param.min_value == 5
        assert param.max_value == 50
        assert param.step == 1

    def test_create_float_parameter(self):
        """Should create float parameter with valid range"""
        param = ParameterSpace(
            name="stop_loss",
            type=ParameterType.FLOAT,
            min_value=0.01,
            max_value=0.1,
            step=0.01
        )
        assert param.name == "stop_loss"
        assert param.type == ParameterType.FLOAT
        assert param.min_value == 0.01
        assert param.max_value == 0.1

    def test_invalid_range_raises_error(self):
        """Should raise error if min > max"""
        with pytest.raises(ValueError, match="min_value must be less than or equal to max_value"):
            ParameterSpace(
                name="period",
                type=ParameterType.INTEGER,
                min_value=100,
                max_value=50
            )

    def test_get_grid_values_integer(self):
        """Should generate integer grid values"""
        param = ParameterSpace(
            name="period",
            type=ParameterType.INTEGER,
            min_value=5,
            max_value=15,
            step=5
        )
        values = param.get_grid_values()
        assert values == [5, 10, 15]

    def test_get_grid_values_float(self):
        """Should generate float grid values"""
        param = ParameterSpace(
            name="threshold",
            type=ParameterType.FLOAT,
            min_value=0.0,
            max_value=1.0,
            step=0.5
        )
        values = param.get_grid_values()
        assert len(values) == 3
        assert values[0] == pytest.approx(0.0)
        assert values[1] == pytest.approx(0.5)
        assert values[2] == pytest.approx(1.0)

    def test_sample_random_value_integer(self):
        """Should sample random integer value within range"""
        param = ParameterSpace(
            name="period",
            type=ParameterType.INTEGER,
            min_value=10,
            max_value=20
        )
        value = param.sample_random_value()
        assert isinstance(value, int)
        assert 10 <= value <= 20

    def test_sample_random_value_float(self):
        """Should sample random float value within range"""
        param = ParameterSpace(
            name="threshold",
            type=ParameterType.FLOAT,
            min_value=0.0,
            max_value=1.0
        )
        value = param.sample_random_value()
        assert isinstance(value, float)
        assert 0.0 <= value <= 1.0


class TestObjectiveFunction:
    """Test ObjectiveFunction domain model"""

    def test_create_sharpe_ratio_objective(self):
        """Should create Sharpe ratio objective function"""
        obj = ObjectiveFunction.sharpe_ratio()
        assert obj.name == "sharpe_ratio"
        assert obj.maximize is True

    def test_create_total_return_objective(self):
        """Should create total return objective function"""
        obj = ObjectiveFunction.total_return()
        assert obj.name == "total_return"
        assert obj.maximize is True

    def test_create_max_drawdown_objective(self):
        """Should create max drawdown objective function"""
        obj = ObjectiveFunction.max_drawdown()
        assert obj.name == "max_drawdown"
        assert obj.maximize is False  # We want to minimize drawdown

    def test_create_custom_objective(self):
        """Should create custom objective function"""
        obj = ObjectiveFunction(
            name="custom_metric",
            maximize=True,
            metric_name="profit_factor"
        )
        assert obj.name == "custom_metric"
        assert obj.maximize is True
        assert obj.metric_name == "profit_factor"


class TestOptimizationResult:
    """Test OptimizationResult domain model"""

    def test_create_optimization_result(self):
        """Should create optimization result with all fields"""
        result = OptimizationResult(
            parameters={"fast_period": 10, "slow_period": 50},
            objective_value=1.5,
            metrics={
                "sharpe_ratio": 1.5,
                "total_return": 25.3,
                "max_drawdown": -12.5
            },
            backtest_count=100,
            optimization_time=45.2
        )
        assert result.parameters == {"fast_period": 10, "slow_period": 50}
        assert result.objective_value == 1.5
        assert result.metrics["sharpe_ratio"] == 1.5
        assert result.backtest_count == 100
        assert result.optimization_time == 45.2

    def test_result_comparison_maximize(self):
        """Should correctly compare results when maximizing"""
        result1 = OptimizationResult(
            parameters={"period": 10},
            objective_value=1.5,
            metrics={},
            backtest_count=1,
            optimization_time=1.0,
            maximize=True
        )
        result2 = OptimizationResult(
            parameters={"period": 20},
            objective_value=2.0,
            metrics={},
            backtest_count=1,
            optimization_time=1.0,
            maximize=True
        )
        assert result2.is_better_than(result1) is True
        assert result1.is_better_than(result2) is False

    def test_result_comparison_minimize(self):
        """Should correctly compare results when minimizing"""
        result1 = OptimizationResult(
            parameters={"period": 10},
            objective_value=-15.0,
            metrics={},
            backtest_count=1,
            optimization_time=1.0,
            maximize=False
        )
        result2 = OptimizationResult(
            parameters={"period": 20},
            objective_value=-10.0,
            metrics={},
            backtest_count=1,
            optimization_time=1.0,
            maximize=False
        )
        assert result2.is_better_than(result1) is True
        assert result1.is_better_than(result2) is False
