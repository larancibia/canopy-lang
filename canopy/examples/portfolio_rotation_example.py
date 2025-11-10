"""
Example: Portfolio Rotation Strategy

This example demonstrates a momentum rotation strategy that rotates
into the top N performing assets.
"""

import pandas as pd
import numpy as np
from canopy.domain.portfolio_strategy import RotationStrategy
from canopy.domain.timeseries import TimeSeries
from canopy.application.run_portfolio_backtest import run_portfolio_backtest
from canopy.domain import metrics


def create_sample_data():
    """Create sample multi-asset time series data."""
    np.random.seed(42)
    dates = pd.date_range("2023-01-01", periods=252, freq="D")

    def create_asset(symbol, base_price, drift, volatility):
        """Create a single asset with price dynamics."""
        returns = np.random.normal(drift, volatility, len(dates))
        prices = base_price * np.exp(np.cumsum(returns))

        # Create valid OHLC
        close = prices
        open_p = close * (1 + np.random.uniform(-0.005, 0.005, len(dates)))
        high = np.maximum(close, open_p) * (1 + np.abs(np.random.uniform(0, 0.01, len(dates))))
        low = np.minimum(close, open_p) * (1 - np.abs(np.random.uniform(0, 0.01, len(dates))))

        return TimeSeries(
            symbol=symbol,
            open=pd.Series(open_p, index=dates),
            high=pd.Series(high, index=dates),
            low=pd.Series(low, index=dates),
            close=pd.Series(close, index=dates),
            volume=pd.Series(np.random.randint(1000000, 5000000, len(dates)), index=dates),
        )

    # Create a universe of assets with different characteristics
    timeseries_data = {
        "TECH": create_asset("TECH", 100, 0.0008, 0.02),     # High growth tech
        "VALUE": create_asset("VALUE", 50, 0.0004, 0.015),   # Steady value
        "GROWTH": create_asset("GROWTH", 150, 0.0006, 0.018), # Growth stock
        "DIVIDEND": create_asset("DIVIDEND", 75, 0.0003, 0.01), # Low vol dividend
        "SMALL": create_asset("SMALL", 25, 0.0007, 0.025),   # Small cap volatile
    }

    return timeseries_data


def main():
    """Run the rotation strategy example."""
    print("=" * 70)
    print("Portfolio Rotation Strategy Example")
    print("=" * 70)

    # Create sample data
    print("\n1. Creating sample data for 5 assets...")
    timeseries_data = create_sample_data()
    print(f"   Created {len(timeseries_data)} assets with 252 days of data")

    # Define rotation strategy
    print("\n2. Creating rotation strategy...")
    strategy = RotationStrategy(
        name="Top 3 Momentum Rotation",
        symbols=["TECH", "VALUE", "GROWTH", "DIVIDEND", "SMALL"],
        lookback_period=60,  # 60-day momentum
        top_n=3,             # Hold top 3 performers
        rebalance_frequency=30,  # Rebalance monthly
    )
    print(f"   Strategy: {strategy.name}")
    print(f"   Lookback: {strategy.lookback_period} days")
    print(f"   Top N: {strategy.top_n} assets")
    print(f"   Rebalance: Every {strategy.rebalance_frequency} days")

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

    # Calculate additional metrics
    returns = backtest.equity_curve.pct_change().dropna()
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

        avg_profit = np.mean([t.pnl for t in winning_trades]) if winning_trades else 0
        losing_trades = [t for t in backtest.trades if t.pnl < 0]
        avg_loss = np.mean([t.pnl for t in losing_trades]) if losing_trades else 0

        print(f"   Avg Winning Trade:   ${avg_profit:,.2f}")
        print(f"   Avg Losing Trade:    ${avg_loss:,.2f}")

    print("\n" + "=" * 70)
    print("Backtest Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
