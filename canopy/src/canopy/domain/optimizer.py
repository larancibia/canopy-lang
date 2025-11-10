"""
Portfolio optimizers - Optimization algorithms for portfolio construction.

This module provides various portfolio optimization algorithms including
mean-variance, risk parity, and minimum variance optimization.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
import pandas as pd
import numpy as np
from scipy.optimize import minimize


class PortfolioOptimizer(ABC):
    """
    Abstract base class for portfolio optimizers.

    Optimizers determine optimal portfolio weights based on various criteria.
    """

    @abstractmethod
    def optimize(self, returns: pd.DataFrame, **kwargs) -> Dict[str, float]:
        """
        Optimize portfolio weights.

        Args:
            returns: DataFrame of asset returns (columns = symbols)
            **kwargs: Additional parameters

        Returns:
            Dictionary mapping symbols to optimal weights
        """
        pass


class MeanVarianceOptimizer(PortfolioOptimizer):
    """
    Mean-variance optimizer (Markowitz portfolio optimization).

    Optimizes the trade-off between expected return and variance.
    """

    def __init__(
        self,
        risk_aversion: float = 1.0,
        target_return: Optional[float] = None,
        allow_short: bool = False,
        max_weight: float = 1.0,
        min_weight: float = 0.0,
    ):
        """
        Initialize mean-variance optimizer.

        Args:
            risk_aversion: Risk aversion parameter (higher = more conservative)
            target_return: Target return (if specified, minimize variance for this return)
            allow_short: Whether to allow short positions
            max_weight: Maximum weight for any asset
            min_weight: Minimum weight for any asset
        """
        self.risk_aversion = risk_aversion
        self.target_return = target_return
        self.allow_short = allow_short
        self.max_weight = max_weight
        self.min_weight = min_weight

    def optimize(self, returns: pd.DataFrame, **kwargs) -> Dict[str, float]:
        """
        Optimize portfolio using mean-variance approach.

        Args:
            returns: DataFrame of asset returns

        Returns:
            Optimal weights
        """
        n_assets = len(returns.columns)

        if n_assets == 1:
            return {returns.columns[0]: 1.0}

        # Calculate expected returns and covariance matrix
        expected_returns = returns.mean()
        cov_matrix = returns.cov()

        # Objective function: minimize -return + risk_aversion * variance
        def objective(weights):
            portfolio_return = np.dot(weights, expected_returns)
            portfolio_variance = np.dot(weights, np.dot(cov_matrix, weights))
            return -portfolio_return + self.risk_aversion * portfolio_variance

        # Constraints: weights sum to 1
        constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]

        # Add target return constraint if specified
        if self.target_return is not None:
            constraints.append({
                "type": "eq",
                "fun": lambda w: np.dot(w, expected_returns) - self.target_return
            })

        # Bounds for each weight
        if self.allow_short:
            bounds = [(-1.0, 1.0) for _ in range(n_assets)]
        else:
            bounds = [(self.min_weight, self.max_weight) for _ in range(n_assets)]

        # Initial guess: equal weight
        initial_weights = np.array([1.0 / n_assets] * n_assets)

        # Optimize
        result = minimize(
            objective,
            initial_weights,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={"maxiter": 1000}
        )

        if not result.success:
            # Fall back to equal weight if optimization fails
            return {symbol: 1.0 / n_assets for symbol in returns.columns}

        # Return weights as dictionary
        weights = result.x
        return {symbol: float(max(0, w)) for symbol, w in zip(returns.columns, weights)}


class RiskParityOptimizer(PortfolioOptimizer):
    """
    Risk parity optimizer.

    Allocates capital so each asset contributes equally to portfolio risk.
    """

    def __init__(self, max_iterations: int = 1000):
        """
        Initialize risk parity optimizer.

        Args:
            max_iterations: Maximum optimization iterations
        """
        self.max_iterations = max_iterations

    def optimize(self, returns: pd.DataFrame, **kwargs) -> Dict[str, float]:
        """
        Optimize portfolio using risk parity approach.

        Args:
            returns: DataFrame of asset returns

        Returns:
            Risk parity weights
        """
        n_assets = len(returns.columns)

        if n_assets == 1:
            return {returns.columns[0]: 1.0}

        # Calculate covariance matrix
        cov_matrix = returns.cov().values

        # Objective: minimize squared differences in risk contributions
        def objective(weights):
            # Portfolio variance
            portfolio_var = np.dot(weights, np.dot(cov_matrix, weights))

            # Risk contribution of each asset
            marginal_contrib = np.dot(cov_matrix, weights)
            risk_contrib = weights * marginal_contrib

            # Target risk contribution (equal for all assets)
            target_risk = portfolio_var / n_assets

            # Sum of squared differences from target
            return np.sum((risk_contrib - target_risk) ** 2)

        # Constraints: weights sum to 1, all positive
        constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]
        bounds = [(0.0, 1.0) for _ in range(n_assets)]

        # Initial guess: equal weight
        initial_weights = np.array([1.0 / n_assets] * n_assets)

        # Optimize
        result = minimize(
            objective,
            initial_weights,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={"maxiter": self.max_iterations}
        )

        if not result.success:
            # Fall back to inverse volatility weighting
            volatilities = np.sqrt(np.diag(cov_matrix))
            inv_vol = 1.0 / volatilities
            weights = inv_vol / inv_vol.sum()
        else:
            weights = result.x

        return {symbol: float(w) for symbol, w in zip(returns.columns, weights)}


class MinimumVarianceOptimizer(PortfolioOptimizer):
    """
    Minimum variance optimizer.

    Finds the portfolio with the lowest possible variance.
    """

    def __init__(self, allow_short: bool = False):
        """
        Initialize minimum variance optimizer.

        Args:
            allow_short: Whether to allow short positions
        """
        self.allow_short = allow_short

    def optimize(self, returns: pd.DataFrame, **kwargs) -> Dict[str, float]:
        """
        Optimize portfolio to minimize variance.

        Args:
            returns: DataFrame of asset returns

        Returns:
            Minimum variance weights
        """
        n_assets = len(returns.columns)

        if n_assets == 1:
            return {returns.columns[0]: 1.0}

        # Calculate covariance matrix
        cov_matrix = returns.cov().values

        # Objective: minimize portfolio variance
        def objective(weights):
            return np.dot(weights, np.dot(cov_matrix, weights))

        # Constraints: weights sum to 1
        constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]

        # Bounds
        if self.allow_short:
            bounds = [(-1.0, 1.0) for _ in range(n_assets)]
        else:
            bounds = [(0.0, 1.0) for _ in range(n_assets)]

        # Initial guess: equal weight
        initial_weights = np.array([1.0 / n_assets] * n_assets)

        # Optimize
        result = minimize(
            objective,
            initial_weights,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={"maxiter": 1000}
        )

        if not result.success:
            # Fall back to equal weight
            return {symbol: 1.0 / n_assets for symbol in returns.columns}

        weights = result.x
        return {symbol: float(w) for symbol, w in zip(returns.columns, weights)}


class MaxSharpeOptimizer(PortfolioOptimizer):
    """
    Maximum Sharpe ratio optimizer.

    Finds the portfolio with the highest Sharpe ratio (return/risk).
    """

    def __init__(
        self,
        risk_free_rate: float = 0.0,
        allow_short: bool = False
    ):
        """
        Initialize max Sharpe optimizer.

        Args:
            risk_free_rate: Risk-free rate per period
            allow_short: Whether to allow short positions
        """
        self.risk_free_rate = risk_free_rate
        self.allow_short = allow_short

    def optimize(self, returns: pd.DataFrame, **kwargs) -> Dict[str, float]:
        """
        Optimize portfolio to maximize Sharpe ratio.

        Args:
            returns: DataFrame of asset returns

        Returns:
            Maximum Sharpe ratio weights
        """
        n_assets = len(returns.columns)

        if n_assets == 1:
            return {returns.columns[0]: 1.0}

        # Calculate expected returns and covariance matrix
        expected_returns = returns.mean().values
        cov_matrix = returns.cov().values

        # Objective: maximize Sharpe ratio = minimize negative Sharpe ratio
        def objective(weights):
            portfolio_return = np.dot(weights, expected_returns)
            portfolio_std = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))

            if portfolio_std == 0:
                return 1e10

            sharpe = (portfolio_return - self.risk_free_rate) / portfolio_std
            return -sharpe  # Minimize negative Sharpe

        # Constraints: weights sum to 1
        constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]

        # Bounds
        if self.allow_short:
            bounds = [(-1.0, 1.0) for _ in range(n_assets)]
        else:
            bounds = [(0.0, 1.0) for _ in range(n_assets)]

        # Initial guess: equal weight
        initial_weights = np.array([1.0 / n_assets] * n_assets)

        # Optimize
        result = minimize(
            objective,
            initial_weights,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={"maxiter": 1000}
        )

        if not result.success:
            # Fall back to equal weight
            return {symbol: 1.0 / n_assets for symbol in returns.columns}

        weights = result.x
        return {symbol: float(w) for symbol, w in zip(returns.columns, weights)}


class EqualWeightOptimizer(PortfolioOptimizer):
    """
    Equal weight optimizer (1/N portfolio).

    Simple baseline that allocates equally to all assets.
    """

    def optimize(self, returns: pd.DataFrame, **kwargs) -> Dict[str, float]:
        """
        Create equal weight portfolio.

        Args:
            returns: DataFrame of asset returns

        Returns:
            Equal weights
        """
        n_assets = len(returns.columns)
        weight = 1.0 / n_assets

        return {symbol: weight for symbol in returns.columns}
