"""
Performance metrics calculations for backtesting.

This module provides pure functions for calculating various trading performance
metrics following hexagonal architecture principles (no external dependencies).
"""

import pandas as pd
import numpy as np
from typing import List
from pydantic import BaseModel
from canopy.domain.backtest import Trade


def sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
    """
    Calculate Sharpe ratio.

    The Sharpe ratio measures risk-adjusted return by comparing excess return
    to the standard deviation of returns.

    Args:
        returns: Series of periodic returns
        risk_free_rate: Risk-free rate per period (default 0.0)

    Returns:
        Sharpe ratio (higher is better, typically >1 is good)
    """
    if len(returns) == 0:
        return 0.0

    excess_returns = returns - risk_free_rate
    std_dev = excess_returns.std()

    if std_dev == 0 or pd.isna(std_dev):
        return 0.0

    return float(excess_returns.mean() / std_dev)


def sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
    """
    Calculate Sortino ratio.

    Similar to Sharpe ratio but only considers downside deviation,
    ignoring upside volatility.

    Args:
        returns: Series of periodic returns
        risk_free_rate: Risk-free rate per period (default 0.0)

    Returns:
        Sortino ratio (higher is better)
    """
    if len(returns) == 0:
        return 0.0

    excess_returns = returns - risk_free_rate
    downside_returns = excess_returns[excess_returns < 0.0]

    if len(downside_returns) == 0:
        return 0.0

    downside_std = downside_returns.std()

    if downside_std == 0 or pd.isna(downside_std):
        return 0.0

    return float(excess_returns.mean() / downside_std)


def max_drawdown(equity_curve: pd.Series) -> float:
    """
    Calculate maximum drawdown percentage.

    Maximum drawdown is the largest peak-to-trough decline in the equity curve.

    Args:
        equity_curve: Series representing equity over time

    Returns:
        Maximum drawdown as a percentage (negative value, e.g., -15.5 for 15.5% drawdown)
    """
    if len(equity_curve) == 0:
        return 0.0

    # Calculate running maximum
    running_max = equity_curve.expanding().max()

    # Calculate drawdown at each point
    drawdown = (equity_curve - running_max) / running_max * 100.0

    # Return the minimum (most negative) drawdown
    mdd = float(drawdown.min())

    return mdd if not pd.isna(mdd) else 0.0


def max_drawdown_duration(equity_curve: pd.Series) -> int:
    """
    Calculate maximum drawdown duration in periods.

    This measures the longest time it takes to recover from a drawdown
    back to a new high.

    Args:
        equity_curve: Series representing equity over time

    Returns:
        Maximum drawdown duration in periods
    """
    if len(equity_curve) == 0:
        return 0

    # Calculate running maximum
    running_max = equity_curve.expanding().max()

    # Find periods where we're below the running max (underwater)
    underwater = equity_curve < running_max

    if not underwater.any():
        return 0

    # Find consecutive underwater periods
    max_duration = 0
    current_duration = 0

    for is_underwater in underwater:
        if is_underwater:
            current_duration += 1
            max_duration = max(max_duration, current_duration)
        else:
            current_duration = 0

    return max_duration


def win_rate(trades: List[Trade]) -> float:
    """
    Calculate win rate (percentage of winning trades).

    Args:
        trades: List of Trade objects

    Returns:
        Win rate as a percentage (0-100)
    """
    if len(trades) == 0:
        return 0.0

    winning_trades = sum(1 for trade in trades if trade.pnl > 0)

    return (winning_trades / len(trades)) * 100.0


def profit_factor(trades: List[Trade]) -> float:
    """
    Calculate profit factor (gross profit / gross loss).

    Profit factor measures the ratio of total winning trade profits
    to total losing trade losses.

    Args:
        trades: List of Trade objects

    Returns:
        Profit factor (>1 means profitable, e.g., 2.0 means $2 profit for every $1 loss)
    """
    if len(trades) == 0:
        return 0.0

    gross_profit = sum(trade.pnl for trade in trades if trade.pnl > 0)
    gross_loss = abs(sum(trade.pnl for trade in trades if trade.pnl < 0))

    if gross_loss == 0:
        return 0.0

    return gross_profit / gross_loss


def calmar_ratio(returns: pd.Series) -> float:
    """
    Calculate Calmar ratio (annualized return / max drawdown).

    The Calmar ratio measures return relative to downside risk.

    Args:
        returns: Series of periodic returns

    Returns:
        Calmar ratio (higher is better)
    """
    if len(returns) == 0:
        return 0.0

    # Calculate annualized return (assuming daily returns, 252 trading days)
    total_return = (1 + returns).prod() - 1
    n_periods = len(returns)
    periods_per_year = 252  # Assume daily data

    if n_periods < periods_per_year:
        # If less than a year of data, scale proportionally
        annualized_return = total_return * (periods_per_year / n_periods)
    else:
        # Compound annual growth rate
        years = n_periods / periods_per_year
        annualized_return = (1 + total_return) ** (1 / years) - 1

    # Calculate equity curve from returns
    equity_curve = (1 + returns).cumprod() * 10000  # Start with $10,000

    # Calculate max drawdown
    mdd = max_drawdown(equity_curve)

    if mdd == 0 or mdd >= 0:
        return 0.0

    # Calmar ratio = annual return / abs(max drawdown)
    return float(annualized_return * 100.0 / abs(mdd))


class PerformanceMetrics(BaseModel):
    """
    Container for all performance metrics.

    This class aggregates all key performance indicators from a backtest,
    providing a comprehensive view of strategy performance.
    """

    total_return: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    max_drawdown_duration: int
    win_rate: float
    profit_factor: float
    calmar_ratio: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    average_win: float
    average_loss: float
