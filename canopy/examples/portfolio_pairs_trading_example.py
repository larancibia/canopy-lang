"""
Example: Pairs Trading Strategy

This example demonstrates a pairs trading strategy that trades the spread
between two correlated assets.
"""

import pandas as pd
import numpy as np
from canopy.domain.portfolio_strategy import PairsTradingStrategy
from canopy.domain.timeseries import TimeSeries
from canopy.application.run_portfolio_backtest import run_portfolio_backtest
from canopy.domain import metrics


def create_correlated_pairs():
    """Create two correlated assets for pairs trading."""
    np.random.seed(42)
    dates = pd.date_range("2023-01-01", periods=252, freq="D")

    # Create a common factor
    common_factor = np.cumsum(np.random.normal(0, 0.01, len(dates)))

    # Asset 1: follows common factor closely
    asset1_returns = common_factor + np.random.normal(0, 0.005, len(dates))
    asset1_prices = 100 * np.exp(asset1_returns)

    # Asset 2: follows common factor with different scale
    asset2_returns = common_factor * 1.2 + np.random.normal(0, 0.005, len(dates))
    asset2_prices = 150 * np.exp(asset2_returns)

    def create_ts(symbol, prices, dates_idx):
        """Create TimeSeries with valid OHLC."""
        close = prices
        open_p = close * (1 + np.random.uniform(-0.005, 0.005, len(dates_idx)))
        high = np.maximum(close, open_p) * (1 + np.abs(np.random.uniform(0, 0.008, len(dates_idx))))
        low = np.minimum(close, open_p) * (1 - np.abs(np.random.uniform(0, 0.008, len(dates_idx))))

        return TimeSeries(
            symbol=symbol,
            open=pd.Series(open_p, index=dates_idx),
            high=pd.Series(high, index=dates_idx),
            low=pd.Series(low, index=dates_idx),
            close=pd.Series(close, index=dates_idx),
            volume=pd.Series(np.random.randint(1000000, 3000000, len(dates_idx)), index=dates_idx),
        )

    return {
        "ASSET_A": create_ts("ASSET_A", asset1_prices, dates),
        "ASSET_B": create_ts("ASSET_B", asset2_prices, dates),
    }


def main():
    """Run the pairs trading strategy example."""
    print("=" * 70)
    print("Pairs Trading Strategy Example")
    print("=" * 70)

    # Create correlated pairs
    print("\n1. Creating correlated pair of assets...")
    timeseries_data = create_correlated_pairs()

    # Calculate correlation
    returns_a = timeseries_data["ASSET_A"].close.pct_change().dropna()
    returns_b = timeseries_data["ASSET_B"].close.pct_change().dropna()
    correlation = returns_a.corr(returns_b)

    print(f"   Asset A and Asset B correlation: {correlation:.3f}")
    print(f"   Data period: {len(timeseries_data['ASSET_A'].close)} days")

    # Define pairs trading strategy
    print("\n2. Creating pairs trading strategy...")
    strategy = PairsTradingStrategy(
        name="Mean Reversion Pairs",
        symbol1="ASSET_A",
        symbol2="ASSET_B",
        lookback_period=30,    # 30-day rolling window for spread
        entry_threshold=2.0,   # Enter when z-score > 2 or < -2
        exit_threshold=0.5,    # Exit when z-score crosses 0.5
    )

    print(f"   Strategy: {strategy.name}")
    print(f"   Lookback Period: {strategy.lookback_period} days")
    print(f"   Entry Threshold: ±{strategy.entry_threshold} std dev")
    print(f"   Exit Threshold: ±{strategy.exit_threshold} std dev")

    # Run backtest
    print("\n3. Running backtest...")
    backtest = run_portfolio_backtest(
        strategy=strategy,
        timeseries_data=timeseries_data,
        initial_capital=100000.0,
        commission=0.001,  # 0.1% commission
        slippage=0.001,    # 0.1% slippage
    )

    # Calculate metrics
    print("\n4. Performance Results:")
    print("-" * 70)
    print(f"   Total Return:        {backtest.total_return():.2f}%")
    print(f"   Final Equity:        ${backtest.final_equity():,.2f}")
    print(f"   Initial Capital:     ${backtest.initial_capital:,.2f}")

    returns = backtest.equity_curve.pct_change().dropna()
    if len(returns) > 0:
        sharpe = metrics.sharpe_ratio(returns)
        max_dd = metrics.max_drawdown(backtest.equity_curve)
        sortino = metrics.sortino_ratio(returns)

        print(f"\n   Sharpe Ratio:        {sharpe:.3f}")
        print(f"   Sortino Ratio:       {sortino:.3f}")
        print(f"   Max Drawdown:        {max_dd:.2f}%")

    print(f"\n   Total Trades:        {len(backtest.trades)}")

    if backtest.trades:
        winning_trades = [t for t in backtest.trades if t.pnl > 0]
        win_rate_pct = (len(winning_trades) / len(backtest.trades)) * 100
        print(f"   Win Rate:            {win_rate_pct:.1f}%")

        total_pnl = sum(t.pnl for t in backtest.trades)
        print(f"   Total P&L:           ${total_pnl:,.2f}")

    print("\n" + "=" * 70)
    print("Backtest Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
