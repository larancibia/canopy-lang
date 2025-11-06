"""
Custom Indicator Example

This example shows how to create a custom technical indicator
and use it within the Canopy framework.
"""

import numpy as np
import pandas as pd
from typing import List


def custom_momentum_indicator(
    close: pd.Series, fast_period: int = 10, slow_period: int = 30
) -> pd.Series:
    """
    Custom momentum indicator combining rate of change and moving averages.

    Args:
        close: Closing prices
        fast_period: Fast period for ROC
        slow_period: Slow period for moving average

    Returns:
        Custom momentum score
    """
    # Calculate rate of change
    roc = close.pct_change(fast_period) * 100

    # Calculate moving average of ROC
    roc_ma = roc.rolling(window=slow_period).mean()

    # Calculate z-score for normalization
    roc_std = roc.rolling(window=slow_period).std()
    momentum_score = (roc - roc_ma) / roc_std

    return momentum_score


def adaptive_moving_average(
    close: pd.Series, fast_period: int = 2, slow_period: int = 30
) -> pd.Series:
    """
    Adaptive Moving Average (KAMA-like indicator).

    Adjusts smoothing based on market efficiency ratio.

    Args:
        close: Closing prices
        fast_period: Fast EMA period
        slow_period: Slow EMA period

    Returns:
        Adaptive moving average
    """
    # Calculate efficiency ratio
    change = abs(close - close.shift(slow_period))
    volatility = abs(close - close.shift(1)).rolling(window=slow_period).sum()
    efficiency_ratio = change / volatility

    # Calculate smoothing constant
    fast_sc = 2 / (fast_period + 1)
    slow_sc = 2 / (slow_period + 1)
    sc = (efficiency_ratio * (fast_sc - slow_sc) + slow_sc) ** 2

    # Apply adaptive smoothing
    ama = pd.Series(index=close.index, dtype=float)
    ama.iloc[slow_period] = close.iloc[slow_period]

    for i in range(slow_period + 1, len(close)):
        ama.iloc[i] = ama.iloc[i - 1] + sc.iloc[i] * (close.iloc[i] - ama.iloc[i - 1])

    return ama


def volume_weighted_rsi(
    close: pd.Series, volume: pd.Series, period: int = 14
) -> pd.Series:
    """
    Volume-Weighted RSI.

    Traditional RSI weighted by trading volume.

    Args:
        close: Closing prices
        volume: Trading volume
        period: RSI period

    Returns:
        Volume-weighted RSI values
    """
    # Calculate price changes
    delta = close.diff()

    # Separate gains and losses
    gains = delta.where(delta > 0, 0) * volume
    losses = -delta.where(delta < 0, 0) * volume

    # Calculate average gains and losses
    avg_gains = gains.rolling(window=period).mean()
    avg_losses = losses.rolling(window=period).mean()

    # Calculate RS and RSI
    rs = avg_gains / avg_losses
    vw_rsi = 100 - (100 / (1 + rs))

    return vw_rsi


def trend_strength_indicator(close: pd.Series, period: int = 20) -> pd.Series:
    """
    Trend Strength Indicator.

    Measures the strength of a trend using linear regression.

    Args:
        close: Closing prices
        period: Period for trend calculation

    Returns:
        Trend strength score (0-100)
    """
    trend_strength = pd.Series(index=close.index, dtype=float)

    for i in range(period, len(close)):
        # Get price window
        y = close.iloc[i - period : i].values
        x = np.arange(len(y))

        # Calculate linear regression
        slope, intercept = np.polyfit(x, y, 1)

        # Calculate R-squared
        y_pred = slope * x + intercept
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)

        # Trend strength (0-100)
        trend_strength.iloc[i] = r_squared * 100

    return trend_strength


# Example: Using custom indicators in a strategy
def example_strategy_with_custom_indicators():
    """
    Example strategy using custom indicators.
    """
    from canopy.adapters.data.yahoo_provider import YahooProvider
    from canopy.domain.timeseries import TimeSeries

    # Fetch data
    provider = YahooProvider()
    data = provider.fetch_data("AAPL", "2022-01-01", "2023-12-31")

    # Convert to pandas
    df = pd.DataFrame(
        {
            "close": [bar.close for bar in data.bars],
            "volume": [bar.volume for bar in data.bars],
        }
    )

    # Calculate custom indicators
    momentum = custom_momentum_indicator(df["close"])
    ama = adaptive_moving_average(df["close"])
    vw_rsi = volume_weighted_rsi(df["close"], df["volume"])
    trend_strength = trend_strength_indicator(df["close"])

    # Generate signals
    signals = []
    for i in range(len(df)):
        # Buy when momentum is positive, price above AMA, and strong trend
        if (
            momentum.iloc[i] > 0.5
            and df["close"].iloc[i] > ama.iloc[i]
            and trend_strength.iloc[i] > 60
        ):
            signals.append("BUY")
        # Sell when momentum turns negative or weak trend
        elif momentum.iloc[i] < -0.5 or trend_strength.iloc[i] < 30:
            signals.append("SELL")
        else:
            signals.append("HOLD")

    return signals


if __name__ == "__main__":
    # Test custom indicators
    print("Testing custom indicators...")

    # Generate sample data
    np.random.seed(42)
    dates = pd.date_range("2023-01-01", periods=100)
    close_prices = pd.Series(100 + np.cumsum(np.random.randn(100) * 2), index=dates)
    volume = pd.Series(np.random.randint(1000000, 5000000, 100), index=dates)

    # Test each indicator
    print("\n1. Custom Momentum Indicator:")
    momentum = custom_momentum_indicator(close_prices)
    print(f"   Latest value: {momentum.iloc[-1]:.2f}")

    print("\n2. Adaptive Moving Average:")
    ama = adaptive_moving_average(close_prices)
    print(f"   Latest value: {ama.iloc[-1]:.2f}")

    print("\n3. Volume-Weighted RSI:")
    vw_rsi = volume_weighted_rsi(close_prices, volume)
    print(f"   Latest value: {vw_rsi.iloc[-1]:.2f}")

    print("\n4. Trend Strength Indicator:")
    trend = trend_strength_indicator(close_prices)
    print(f"   Latest value: {trend.iloc[-1]:.2f}")

    print("\nCustom indicators calculated successfully!")
