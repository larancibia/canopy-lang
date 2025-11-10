"""
Tests for Monte Carlo simulation domain models.

Monte Carlo simulation helps estimate confidence intervals
and worst-case scenarios by randomizing trade sequences.
"""

import pytest
import pandas as pd
import numpy as np
from canopy.domain.monte_carlo import (
    MonteCarloConfig,
    MonteCarloResult,
    ConfidenceInterval,
)


class TestMonteCarloConfig:
    """Test MonteCarloConfig domain model"""

    def test_create_monte_carlo_config(self):
        """Should create Monte Carlo configuration"""
        config = MonteCarloConfig(
            n_simulations=1000,
            confidence_level=0.95,
            random_seed=42
        )
        assert config.n_simulations == 1000
        assert config.confidence_level == 0.95
        assert config.random_seed == 42

    def test_default_values(self):
        """Should use default values when not specified"""
        config = MonteCarloConfig(n_simulations=500)
        assert config.confidence_level == 0.95
        assert config.random_seed is None

    def test_invalid_simulations_raises_error(self):
        """Should raise error if n_simulations is invalid"""
        with pytest.raises(ValueError, match="n_simulations must be positive"):
            MonteCarloConfig(n_simulations=0)

    def test_invalid_confidence_level_raises_error(self):
        """Should raise error if confidence_level is out of range"""
        with pytest.raises(ValueError, match="confidence_level must be between 0 and 1"):
            MonteCarloConfig(n_simulations=100, confidence_level=1.5)


class TestConfidenceInterval:
    """Test ConfidenceInterval domain model"""

    def test_create_confidence_interval(self):
        """Should create confidence interval"""
        ci = ConfidenceInterval(
            lower=10.0,
            upper=30.0,
            median=20.0,
            confidence_level=0.95
        )
        assert ci.lower == 10.0
        assert ci.upper == 30.0
        assert ci.median == 20.0
        assert ci.confidence_level == 0.95

    def test_range_calculation(self):
        """Should calculate range correctly"""
        ci = ConfidenceInterval(
            lower=10.0,
            upper=30.0,
            median=20.0,
            confidence_level=0.95
        )
        assert ci.range() == 20.0


class TestMonteCarloResult:
    """Test MonteCarloResult domain model"""

    def test_create_monte_carlo_result(self):
        """Should create Monte Carlo result with all fields"""
        simulations = [15.0, 20.0, 25.0, 30.0, 35.0]
        result = MonteCarloResult(
            simulated_returns=simulations,
            confidence_interval=ConfidenceInterval(
                lower=15.0,
                upper=35.0,
                median=25.0,
                confidence_level=0.95
            ),
            worst_case_return=-10.0,
            best_case_return=50.0,
            expected_return=25.0,
            risk_of_ruin=0.05,
            n_simulations=5
        )
        assert len(result.simulated_returns) == 5
        assert result.expected_return == 25.0
        assert result.risk_of_ruin == 0.05

    def test_calculate_percentile(self):
        """Should calculate percentile correctly"""
        simulations = list(range(0, 101))  # 0 to 100
        result = MonteCarloResult(
            simulated_returns=simulations,
            confidence_interval=ConfidenceInterval(
                lower=5.0,
                upper=95.0,
                median=50.0,
                confidence_level=0.9
            ),
            worst_case_return=0.0,
            best_case_return=100.0,
            expected_return=50.0,
            risk_of_ruin=0.0,
            n_simulations=101
        )

        # 10th percentile should be around 10
        p10 = result.percentile(0.1)
        assert 9.0 <= p10 <= 11.0

        # 50th percentile (median) should be around 50
        p50 = result.percentile(0.5)
        assert 49.0 <= p50 <= 51.0

        # 90th percentile should be around 90
        p90 = result.percentile(0.9)
        assert 89.0 <= p90 <= 91.0

    def test_probability_of_loss(self):
        """Should calculate probability of loss"""
        # 20 negative, 80 positive out of 100
        simulations = [-10.0] * 20 + [5.0] * 80
        result = MonteCarloResult(
            simulated_returns=simulations,
            confidence_interval=ConfidenceInterval(
                lower=-10.0,
                upper=5.0,
                median=2.0,
                confidence_level=0.9
            ),
            worst_case_return=-10.0,
            best_case_return=5.0,
            expected_return=2.0,
            risk_of_ruin=0.0,
            n_simulations=100
        )

        prob_loss = result.probability_of_loss()
        assert prob_loss == pytest.approx(0.2)  # 20%

    def test_sharpe_statistics(self):
        """Should calculate Sharpe ratio statistics"""
        # Simulate Sharpe ratios
        sharpe_values = [1.0, 1.5, 2.0, 2.5, 3.0]
        result = MonteCarloResult(
            simulated_returns=sharpe_values,
            confidence_interval=ConfidenceInterval(
                lower=1.0,
                upper=3.0,
                median=2.0,
                confidence_level=0.95
            ),
            worst_case_return=1.0,
            best_case_return=3.0,
            expected_return=2.0,
            risk_of_ruin=0.0,
            n_simulations=5
        )

        mean = result.mean()
        std = result.std()

        assert mean == pytest.approx(2.0)
        assert std > 0  # Should have some variance
