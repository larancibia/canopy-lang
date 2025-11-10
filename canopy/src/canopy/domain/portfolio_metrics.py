"""
Portfolio metrics - Performance metrics for multi-asset portfolios.

This module provides metrics specific to portfolio management including
diversification measures, correlation metrics, turnover, and factor exposures.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional


def portfolio_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
    """
    Calculate portfolio Sharpe ratio.

    Args:
        returns: Series of portfolio returns
        risk_free_rate: Risk-free rate per period

    Returns:
        Sharpe ratio
    """
    if len(returns) == 0:
        return 0.0

    excess_returns = returns - risk_free_rate
    std_dev = excess_returns.std()

    if std_dev == 0 or pd.isna(std_dev):
        return 0.0

    return float(excess_returns.mean() / std_dev)


def diversification_ratio(
    returns: pd.DataFrame,
    weights: Dict[str, float]
) -> float:
    """
    Calculate diversification ratio.

    The diversification ratio measures the ratio of weighted average volatility
    to portfolio volatility. Higher values indicate better diversification.

    DR = (sum of weighted individual volatilities) / portfolio volatility

    Args:
        returns: DataFrame of asset returns (columns = symbols)
        weights: Dictionary of symbol to weight

    Returns:
        Diversification ratio (>= 1.0, higher is better)
    """
    if len(returns) == 0 or len(weights) == 0:
        return 1.0

    # Get symbols that are in both returns and weights
    symbols = [s for s in weights.keys() if s in returns.columns]

    if len(symbols) == 0:
        return 1.0

    # Calculate individual volatilities
    individual_vols = returns[symbols].std()

    # Calculate weighted average volatility
    weights_array = np.array([weights[s] for s in symbols])
    weighted_avg_vol = float(np.sum(individual_vols.values * weights_array))

    # Calculate portfolio volatility
    portfolio_returns = sum(
        returns[symbol] * weights[symbol]
        for symbol in symbols
    )
    portfolio_vol = portfolio_returns.std()

    if portfolio_vol == 0 or pd.isna(portfolio_vol):
        return 1.0

    return weighted_avg_vol / portfolio_vol


def max_position_correlation(returns: pd.DataFrame) -> float:
    """
    Calculate maximum pairwise correlation between positions.

    This metric identifies the highest correlation between any two assets
    in the portfolio, indicating potential concentration risk.

    Args:
        returns: DataFrame of asset returns (columns = symbols)

    Returns:
        Maximum pairwise correlation (0.0 to 1.0)
    """
    if len(returns.columns) <= 1:
        return 0.0

    # Calculate correlation matrix
    corr_matrix = returns.corr()

    # Get upper triangle (excluding diagonal)
    upper_triangle = corr_matrix.where(
        np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
    )

    # Find maximum correlation
    max_corr = upper_triangle.max().max()

    if pd.isna(max_corr):
        return 0.0

    return float(max_corr)


def turnover_rate(
    weights_old: Dict[str, float],
    weights_new: Dict[str, float]
) -> float:
    """
    Calculate portfolio turnover rate.

    Turnover measures the amount of trading required to rebalance the portfolio.
    It's calculated as half the sum of absolute weight changes.

    Args:
        weights_old: Previous portfolio weights
        weights_new: New portfolio weights

    Returns:
        Turnover rate (0.0 to 1.0, where 1.0 = 100% turnover)
    """
    # Get all symbols
    all_symbols = set(weights_old.keys()) | set(weights_new.keys())

    # Calculate sum of absolute differences
    total_change = 0.0
    for symbol in all_symbols:
        old_weight = weights_old.get(symbol, 0.0)
        new_weight = weights_new.get(symbol, 0.0)
        total_change += abs(new_weight - old_weight)

    # Turnover is half the sum of absolute changes
    return total_change / 2.0


def tracking_error(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
    annualize: bool = False,
    periods_per_year: int = 252
) -> float:
    """
    Calculate tracking error (standard deviation of excess returns).

    Tracking error measures how closely a portfolio follows a benchmark.

    Args:
        portfolio_returns: Portfolio returns series
        benchmark_returns: Benchmark returns series
        annualize: Whether to annualize the tracking error
        periods_per_year: Number of periods per year (252 for daily)

    Returns:
        Tracking error (annualized if requested)
    """
    if len(portfolio_returns) == 0 or len(benchmark_returns) == 0:
        return 0.0

    # Calculate excess returns
    excess_returns = portfolio_returns - benchmark_returns

    # Calculate standard deviation
    te = excess_returns.std()

    if pd.isna(te):
        return 0.0

    # Annualize if requested
    if annualize:
        te = te * np.sqrt(periods_per_year)

    return float(te)


def information_ratio(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series
) -> float:
    """
    Calculate information ratio (excess return / tracking error).

    The information ratio measures risk-adjusted excess return relative to
    a benchmark.

    Args:
        portfolio_returns: Portfolio returns series
        benchmark_returns: Benchmark returns series

    Returns:
        Information ratio
    """
    if len(portfolio_returns) == 0 or len(benchmark_returns) == 0:
        return 0.0

    # Calculate excess returns
    excess_returns = portfolio_returns - benchmark_returns

    # Calculate mean excess return
    mean_excess = excess_returns.mean()

    # Calculate tracking error
    te = excess_returns.std()

    if te == 0 or pd.isna(te):
        return 0.0

    return float(mean_excess / te)


def calculate_factor_exposures(
    portfolio_returns: pd.Series,
    factor_returns: pd.DataFrame
) -> Dict[str, float]:
    """
    Calculate portfolio exposures to risk factors.

    Uses linear regression to estimate factor loadings (betas).

    Args:
        portfolio_returns: Portfolio returns series
        factor_returns: DataFrame of factor returns (columns = factor names)

    Returns:
        Dictionary of factor name to exposure (beta)
    """
    if len(portfolio_returns) == 0 or len(factor_returns) == 0:
        return {}

    exposures = {}

    # Calculate exposure to each factor using simple regression
    for factor in factor_returns.columns:
        # Align the series
        aligned_portfolio, aligned_factor = portfolio_returns.align(
            factor_returns[factor], join='inner'
        )

        if len(aligned_portfolio) < 2:
            exposures[factor] = 0.0
            continue

        # Calculate covariance and variance
        covariance = aligned_portfolio.cov(aligned_factor)
        variance = aligned_factor.var()

        if variance == 0 or pd.isna(variance):
            exposures[factor] = 0.0
        else:
            # Beta = Cov(portfolio, factor) / Var(factor)
            exposures[factor] = float(covariance / variance)

    return exposures


def concentration_metric(weights: Dict[str, float]) -> float:
    """
    Calculate portfolio concentration using Herfindahl-Hirschman Index (HHI).

    HHI is the sum of squared weights. Lower values indicate better diversification.

    Args:
        weights: Dictionary of symbol to weight

    Returns:
        HHI (1/n for equal weight, 1.0 for single asset)
    """
    if len(weights) == 0:
        return 0.0

    return float(sum(w ** 2 for w in weights.values()))


def effective_number_of_assets(weights: Dict[str, float]) -> float:
    """
    Calculate effective number of assets (inverse of HHI).

    This metric gives the equivalent number of equally-weighted positions.

    Args:
        weights: Dictionary of symbol to weight

    Returns:
        Effective number of assets (1 to n)
    """
    hhi = concentration_metric(weights)

    if hhi == 0:
        return 0.0

    return 1.0 / hhi


def downside_deviation(
    returns: pd.Series,
    target_return: float = 0.0
) -> float:
    """
    Calculate downside deviation.

    Similar to standard deviation but only considers returns below target.

    Args:
        returns: Series of returns
        target_return: Target return threshold

    Returns:
        Downside deviation
    """
    if len(returns) == 0:
        return 0.0

    # Get returns below target
    downside_returns = returns[returns < target_return]

    if len(downside_returns) == 0:
        return 0.0

    # Calculate squared deviations from target
    squared_deviations = (downside_returns - target_return) ** 2

    # Return square root of mean
    return float(np.sqrt(squared_deviations.mean()))


def ulcer_index(equity_curve: pd.Series) -> float:
    """
    Calculate Ulcer Index (measure of downside risk).

    The Ulcer Index measures the depth and duration of drawdowns.

    Args:
        equity_curve: Series of portfolio equity values

    Returns:
        Ulcer Index (lower is better)
    """
    if len(equity_curve) == 0:
        return 0.0

    # Calculate running maximum
    running_max = equity_curve.expanding().max()

    # Calculate percentage drawdown at each point
    drawdown_pct = ((equity_curve - running_max) / running_max) * 100.0

    # Square the drawdowns
    squared_drawdowns = drawdown_pct ** 2

    # Return square root of mean
    return float(np.sqrt(squared_drawdowns.mean()))
