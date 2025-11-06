"""
Tests for robustness testing domain models.

Robustness testing validates that strategies perform well under
various conditions including noise, parameter changes, and market regimes.
"""

import pytest
import pandas as pd
import numpy as np
from canopy.domain.robustness import (
    SensitivityTestConfig,
    SensitivityTestResult,
    NoiseConfig,
    RegimeType,
)


class TestSensitivityTestConfig:
    """Test SensitivityTestConfig domain model"""

    def test_create_sensitivity_config(self):
        """Should create sensitivity test configuration"""
        config = SensitivityTestConfig(
            parameter_name="fast_period",
            base_value=10,
            perturbation_range=0.2
        )
        assert config.parameter_name == "fast_period"
        assert config.base_value == 10
        assert config.perturbation_range == 0.2

    def test_default_perturbation_range(self):
        """Should use default perturbation range"""
        config = SensitivityTestConfig(
            parameter_name="fast_period",
            base_value=10
        )
        assert config.perturbation_range == 0.1  # 10% default

    def test_get_test_values(self):
        """Should generate test values around base value"""
        config = SensitivityTestConfig(
            parameter_name="period",
            base_value=20,
            perturbation_range=0.2,
            n_steps=5
        )
        values = config.get_test_values()

        # Should have 5 values ranging from 16 to 24 (20 ± 20%)
        assert len(values) == 5
        assert min(values) >= 16
        assert max(values) <= 24
        assert 20 in values  # Base value should be included


class TestSensitivityTestResult:
    """Test SensitivityTestResult domain model"""

    def test_create_sensitivity_result(self):
        """Should create sensitivity test result"""
        result = SensitivityTestResult(
            parameter_name="fast_period",
            base_value=10,
            test_values=[8, 9, 10, 11, 12],
            metric_values=[1.2, 1.4, 1.5, 1.3, 1.1],
            metric_name="sharpe_ratio"
        )
        assert result.parameter_name == "fast_period"
        assert len(result.test_values) == 5
        assert len(result.metric_values) == 5

    def test_sensitivity_score_calculation(self):
        """Should calculate sensitivity score as coefficient of variation"""
        result = SensitivityTestResult(
            parameter_name="period",
            base_value=10,
            test_values=[8, 10, 12],
            metric_values=[1.0, 1.5, 2.0],
            metric_name="sharpe_ratio"
        )

        score = result.sensitivity_score()
        # Coefficient of variation = std / mean
        mean = np.mean([1.0, 1.5, 2.0])
        std = np.std([1.0, 1.5, 2.0])
        expected = std / mean if mean != 0 else 0.0

        assert score == pytest.approx(expected)

    def test_is_robust(self):
        """Should determine if parameter is robust"""
        # Low sensitivity - robust
        result1 = SensitivityTestResult(
            parameter_name="period",
            base_value=10,
            test_values=[8, 10, 12],
            metric_values=[1.5, 1.5, 1.5],  # No variation
            metric_name="sharpe_ratio"
        )
        assert result1.is_robust(threshold=0.2) is True

        # High sensitivity - not robust
        result2 = SensitivityTestResult(
            parameter_name="period",
            base_value=10,
            test_values=[8, 10, 12],
            metric_values=[0.5, 1.5, 2.5],  # High variation
            metric_name="sharpe_ratio"
        )
        assert result2.is_robust(threshold=0.2) is False

    def test_best_value(self):
        """Should find parameter value with best metric"""
        result = SensitivityTestResult(
            parameter_name="period",
            base_value=10,
            test_values=[8, 10, 12],
            metric_values=[1.0, 1.5, 2.0],
            metric_name="sharpe_ratio"
        )

        best = result.best_value()
        assert best == 12  # Highest metric value


class TestNoiseConfig:
    """Test NoiseConfig domain model"""

    def test_create_noise_config(self):
        """Should create noise configuration"""
        config = NoiseConfig(
            noise_level=0.01,
            noise_type="gaussian"
        )
        assert config.noise_level == 0.01
        assert config.noise_type == "gaussian"

    def test_default_noise_type(self):
        """Should use default noise type"""
        config = NoiseConfig(noise_level=0.02)
        assert config.noise_type == "gaussian"

    def test_invalid_noise_level_raises_error(self):
        """Should raise error if noise_level is negative"""
        with pytest.raises(ValueError, match="noise_level must be non-negative"):
            NoiseConfig(noise_level=-0.01)


class TestRegimeType:
    """Test RegimeType enum"""

    def test_regime_types(self):
        """Should define standard market regime types"""
        assert RegimeType.BULL == "bull"
        assert RegimeType.BEAR == "bear"
        assert RegimeType.SIDEWAYS == "sideways"
        assert RegimeType.HIGH_VOLATILITY == "high_volatility"
        assert RegimeType.LOW_VOLATILITY == "low_volatility"
