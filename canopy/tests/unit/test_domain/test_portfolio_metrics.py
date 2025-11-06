"""
Unit tests for portfolio metrics.

Tests for portfolio-level performance metrics including diversification ratio,
correlation metrics, turnover, and factor exposures.
"""

import pytest
import pandas as pd
import numpy as np
from canopy.domain.portfolio_metrics import (
    portfolio_sharpe_ratio,
    diversification_ratio,
    max_position_correlation,
    turnover_rate,
    tracking_error,
    information_ratio,
    calculate_factor_exposures,
)


class TestPortfolioSharpeRatio:
    """Test portfolio Sharpe ratio calculation."""

    def test_sharpe_ratio_basic(self):
        """Test basic Sharpe ratio calculation."""
        returns = pd.Series([0.01, 0.02, -0.01, 0.015, 0.01])

        sharpe = portfolio_sharpe_ratio(returns, risk_free_rate=0.0)

        # Should be same as single asset Sharpe
        assert sharpe > 0
        assert isinstance(sharpe, float)

    def test_sharpe_ratio_with_risk_free(self):
        """Test Sharpe ratio with risk-free rate."""
        returns = pd.Series([0.02, 0.03, 0.01, 0.025, 0.02])
        risk_free = 0.001

        sharpe = portfolio_sharpe_ratio(returns, risk_free_rate=risk_free)

        assert sharpe > 0

    def test_sharpe_ratio_empty_returns(self):
        """Test Sharpe ratio with empty returns."""
        returns = pd.Series([])

        sharpe = portfolio_sharpe_ratio(returns)

        assert sharpe == 0.0


class TestDiversificationRatio:
    """Test diversification ratio calculation."""

    def test_diversification_ratio_basic(self):
        """Test basic diversification ratio."""
        # Create uncorrelated returns
        np.random.seed(42)
        returns = pd.DataFrame({
            "AAPL": np.random.normal(0.001, 0.02, 100),
            "GOOGL": np.random.normal(0.001, 0.02, 100),
            "MSFT": np.random.normal(0.001, 0.02, 100),
        })

        weights = {"AAPL": 0.33, "GOOGL": 0.33, "MSFT": 0.34}

        div_ratio = diversification_ratio(returns, weights)

        # Diversification ratio should be > 1 for uncorrelated assets
        assert div_ratio >= 1.0

    def test_diversification_ratio_single_asset(self):
        """Test diversification ratio with single asset."""
        returns = pd.DataFrame({
            "AAPL": [0.01, 0.02, -0.01, 0.015],
        })

        weights = {"AAPL": 1.0}

        div_ratio = diversification_ratio(returns, weights)

        # Should be 1.0 for single asset (no diversification)
        assert abs(div_ratio - 1.0) < 0.01

    def test_diversification_ratio_perfectly_correlated(self):
        """Test diversification ratio with perfectly correlated assets."""
        returns_base = pd.Series([0.01, 0.02, -0.01, 0.015, 0.01])
        returns = pd.DataFrame({
            "AAPL": returns_base,
            "GOOGL": returns_base * 1.5,  # Perfectly correlated, different scale
        })

        weights = {"AAPL": 0.5, "GOOGL": 0.5}

        div_ratio = diversification_ratio(returns, weights)

        # Should be close to 1.0 for perfectly correlated assets
        assert abs(div_ratio - 1.0) < 0.1


class TestMaxPositionCorrelation:
    """Test maximum position correlation calculation."""

    def test_max_correlation_basic(self):
        """Test basic max correlation."""
        np.random.seed(42)
        returns = pd.DataFrame({
            "AAPL": np.random.normal(0, 0.02, 100),
            "GOOGL": np.random.normal(0, 0.02, 100),
            "MSFT": np.random.normal(0, 0.02, 100),
        })

        max_corr = max_position_correlation(returns)

        # Should be between -1 and 1
        assert -1.0 <= max_corr <= 1.0

    def test_max_correlation_perfect(self):
        """Test max correlation with perfectly correlated assets."""
        returns_base = pd.Series([0.01, 0.02, -0.01, 0.015, 0.01])
        returns = pd.DataFrame({
            "AAPL": returns_base,
            "GOOGL": returns_base,  # Perfectly correlated
            "MSFT": returns_base * 0.8,  # Also perfectly correlated
        })

        max_corr = max_position_correlation(returns)

        # Should be very close to 1.0
        assert max_corr > 0.99

    def test_max_correlation_single_asset(self):
        """Test max correlation with single asset."""
        returns = pd.DataFrame({
            "AAPL": [0.01, 0.02, -0.01, 0.015],
        })

        max_corr = max_position_correlation(returns)

        # Should be 0.0 for single asset
        assert max_corr == 0.0


class TestTurnoverRate:
    """Test turnover rate calculation."""

    def test_turnover_rate_basic(self):
        """Test basic turnover rate."""
        weights_old = {"AAPL": 0.5, "GOOGL": 0.3, "MSFT": 0.2}
        weights_new = {"AAPL": 0.4, "GOOGL": 0.35, "MSFT": 0.25}

        turnover = turnover_rate(weights_old, weights_new)

        # Turnover should be sum of abs differences / 2
        # |0.5-0.4| + |0.3-0.35| + |0.2-0.25| = 0.1 + 0.05 + 0.05 = 0.2
        # 0.2 / 2 = 0.1
        assert abs(turnover - 0.1) < 0.01

    def test_turnover_rate_no_change(self):
        """Test turnover rate with no changes."""
        weights = {"AAPL": 0.5, "GOOGL": 0.3, "MSFT": 0.2}

        turnover = turnover_rate(weights, weights)

        assert turnover == 0.0

    def test_turnover_rate_complete_rebalance(self):
        """Test turnover rate with complete rebalance."""
        weights_old = {"AAPL": 1.0, "GOOGL": 0.0}
        weights_new = {"AAPL": 0.0, "GOOGL": 1.0}

        turnover = turnover_rate(weights_old, weights_new)

        # Complete rebalance should be 1.0 (100% turnover)
        assert abs(turnover - 1.0) < 0.01

    def test_turnover_rate_new_symbols(self):
        """Test turnover rate with new symbols added."""
        weights_old = {"AAPL": 0.5, "GOOGL": 0.5}
        weights_new = {"AAPL": 0.33, "GOOGL": 0.33, "MSFT": 0.34}

        turnover = turnover_rate(weights_old, weights_new)

        # Should handle new symbols correctly
        assert turnover > 0


class TestTrackingError:
    """Test tracking error calculation."""

    def test_tracking_error_basic(self):
        """Test basic tracking error."""
        portfolio_returns = pd.Series([0.01, 0.02, -0.01, 0.015, 0.01])
        benchmark_returns = pd.Series([0.009, 0.018, -0.008, 0.014, 0.011])

        te = tracking_error(portfolio_returns, benchmark_returns)

        assert te > 0
        assert isinstance(te, float)

    def test_tracking_error_identical(self):
        """Test tracking error with identical returns."""
        returns = pd.Series([0.01, 0.02, -0.01, 0.015, 0.01])

        te = tracking_error(returns, returns)

        # Should be 0 or very close to 0
        assert abs(te) < 0.0001

    def test_tracking_error_empty(self):
        """Test tracking error with empty returns."""
        portfolio_returns = pd.Series([])
        benchmark_returns = pd.Series([])

        te = tracking_error(portfolio_returns, benchmark_returns)

        assert te == 0.0


class TestInformationRatio:
    """Test information ratio calculation."""

    def test_information_ratio_basic(self):
        """Test basic information ratio."""
        portfolio_returns = pd.Series([0.02, 0.03, 0.01, 0.025, 0.02])
        benchmark_returns = pd.Series([0.015, 0.025, 0.008, 0.02, 0.018])

        ir = information_ratio(portfolio_returns, benchmark_returns)

        # Portfolio outperforms benchmark, should be positive
        assert ir > 0

    def test_information_ratio_underperform(self):
        """Test information ratio when underperforming."""
        portfolio_returns = pd.Series([0.01, 0.015, 0.005, 0.012, 0.01])
        benchmark_returns = pd.Series([0.02, 0.03, 0.01, 0.025, 0.02])

        ir = information_ratio(portfolio_returns, benchmark_returns)

        # Portfolio underperforms, should be negative
        assert ir < 0

    def test_information_ratio_identical(self):
        """Test information ratio with identical returns."""
        returns = pd.Series([0.01, 0.02, -0.01, 0.015, 0.01])

        ir = information_ratio(returns, returns)

        # Should be 0 or undefined
        assert abs(ir) < 0.0001 or ir == 0.0


class TestFactorExposures:
    """Test factor exposures calculation."""

    def test_factor_exposures_basic(self):
        """Test basic factor exposures."""
        # Create portfolio and factor returns
        portfolio_returns = pd.Series([0.01, 0.02, -0.01, 0.015, 0.01, 0.02])

        factors = pd.DataFrame({
            "market": [0.008, 0.015, -0.008, 0.012, 0.009, 0.016],
            "size": [0.002, 0.005, -0.002, 0.003, 0.001, 0.004],
        })

        exposures = calculate_factor_exposures(portfolio_returns, factors)

        # Should have market and size exposures
        assert "market" in exposures
        assert "size" in exposures
        assert isinstance(exposures["market"], float)
        assert isinstance(exposures["size"], float)

    def test_factor_exposures_market_only(self):
        """Test factor exposures with market factor only."""
        # Create returns highly correlated with market
        market_returns = pd.Series([0.01, 0.02, -0.01, 0.015, 0.01])
        portfolio_returns = market_returns * 1.2  # Beta of 1.2

        factors = pd.DataFrame({
            "market": market_returns,
        })

        exposures = calculate_factor_exposures(portfolio_returns, factors)

        # Market exposure should be close to 1.2
        assert abs(exposures["market"] - 1.2) < 0.1

    def test_factor_exposures_empty(self):
        """Test factor exposures with empty data."""
        portfolio_returns = pd.Series([])
        factors = pd.DataFrame()

        exposures = calculate_factor_exposures(portfolio_returns, factors)

        # Should return empty dict
        assert exposures == {}
