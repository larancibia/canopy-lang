"""
Tests for walk-forward analysis domain models.

Walk-forward analysis is crucial for detecting overfitting by testing
strategies on out-of-sample data.
"""

import pytest
import pandas as pd
import numpy as np
from canopy.domain.walk_forward import (
    WalkForwardConfig,
    WalkForwardWindow,
    WalkForwardResult,
    WindowMode,
)


class TestWalkForwardConfig:
    """Test WalkForwardConfig domain model"""

    def test_create_rolling_window_config(self):
        """Should create rolling window configuration"""
        config = WalkForwardConfig(
            train_size=252,
            test_size=63,
            mode=WindowMode.ROLLING
        )
        assert config.train_size == 252
        assert config.test_size == 63
        assert config.mode == WindowMode.ROLLING

    def test_create_anchored_window_config(self):
        """Should create anchored window configuration"""
        config = WalkForwardConfig(
            train_size=252,
            test_size=63,
            mode=WindowMode.ANCHORED
        )
        assert config.mode == WindowMode.ANCHORED

    def test_invalid_window_sizes_raise_error(self):
        """Should raise error if window sizes are invalid"""
        with pytest.raises(ValueError, match="train_size must be positive"):
            WalkForwardConfig(
                train_size=0,
                test_size=63,
                mode=WindowMode.ROLLING
            )

        with pytest.raises(ValueError, match="test_size must be positive"):
            WalkForwardConfig(
                train_size=252,
                test_size=0,
                mode=WindowMode.ROLLING
            )


class TestWalkForwardWindow:
    """Test WalkForwardWindow domain model"""

    def test_create_walk_forward_window(self):
        """Should create walk-forward window with train/test indices"""
        window = WalkForwardWindow(
            window_id=0,
            train_start=0,
            train_end=252,
            test_start=252,
            test_end=315
        )
        assert window.window_id == 0
        assert window.train_start == 0
        assert window.train_end == 252
        assert window.test_start == 252
        assert window.test_end == 315

    def test_train_size_property(self):
        """Should calculate train size correctly"""
        window = WalkForwardWindow(
            window_id=0,
            train_start=0,
            train_end=252,
            test_start=252,
            test_end=315
        )
        assert window.train_size() == 252

    def test_test_size_property(self):
        """Should calculate test size correctly"""
        window = WalkForwardWindow(
            window_id=0,
            train_start=0,
            train_end=252,
            test_start=252,
            test_end=315
        )
        assert window.test_size() == 63


class TestWalkForwardResult:
    """Test WalkForwardResult domain model"""

    def test_create_walk_forward_result(self):
        """Should create walk-forward result with all metrics"""
        result = WalkForwardResult(
            windows=[],
            in_sample_metrics={
                "sharpe_ratio": 1.8,
                "total_return": 30.0
            },
            out_of_sample_metrics={
                "sharpe_ratio": 1.2,
                "total_return": 18.0
            },
            optimization_parameters={"fast_period": 10, "slow_period": 50},
            total_windows=5
        )
        assert result.in_sample_metrics["sharpe_ratio"] == 1.8
        assert result.out_of_sample_metrics["sharpe_ratio"] == 1.2
        assert result.total_windows == 5

    def test_is_overfit_detection(self):
        """Should detect overfitting when out-of-sample performance degrades"""
        # Not overfit - similar performance
        result1 = WalkForwardResult(
            windows=[],
            in_sample_metrics={"sharpe_ratio": 1.5},
            out_of_sample_metrics={"sharpe_ratio": 1.4},
            optimization_parameters={},
            total_windows=1
        )
        assert result1.is_overfit(threshold=0.3) is False

        # Overfit - significant degradation
        result2 = WalkForwardResult(
            windows=[],
            in_sample_metrics={"sharpe_ratio": 2.0},
            out_of_sample_metrics={"sharpe_ratio": 0.5},
            optimization_parameters={},
            total_windows=1
        )
        assert result2.is_overfit(threshold=0.3) is True

    def test_performance_degradation_calculation(self):
        """Should calculate performance degradation correctly"""
        result = WalkForwardResult(
            windows=[],
            in_sample_metrics={"sharpe_ratio": 2.0},
            out_of_sample_metrics={"sharpe_ratio": 1.5},
            optimization_parameters={},
            total_windows=1
        )
        # Degradation = (2.0 - 1.5) / 2.0 = 0.25
        degradation = result.performance_degradation()
        assert degradation == pytest.approx(0.25)

    def test_performance_degradation_with_zero_in_sample(self):
        """Should handle zero in-sample performance"""
        result = WalkForwardResult(
            windows=[],
            in_sample_metrics={"sharpe_ratio": 0.0},
            out_of_sample_metrics={"sharpe_ratio": 1.0},
            optimization_parameters={},
            total_windows=1
        )
        degradation = result.performance_degradation()
        assert degradation == 0.0  # No degradation can be calculated

    def test_average_metrics_calculation(self):
        """Should calculate average of in-sample and out-of-sample metrics"""
        result = WalkForwardResult(
            windows=[],
            in_sample_metrics={
                "sharpe_ratio": 2.0,
                "total_return": 40.0
            },
            out_of_sample_metrics={
                "sharpe_ratio": 1.0,
                "total_return": 20.0
            },
            optimization_parameters={},
            total_windows=1
        )
        avg = result.average_sharpe_ratio()
        assert avg == pytest.approx(1.5)
