"""
Example: Long-Short Equity Strategy

This example demonstrates a long-short strategy that goes long top performers
and short bottom performers based on momentum.
"""

import pandas as pd
import numpy as np
from canopy.domain.portfolio_strategy import LongShortStrategy
from canopy.domain.timeseries import TimeSeries
from canopy.application.run_portfolio_backtest import run_portfolio_backtest
from canopy.domain import metrics
from canopy.domain.portfolio_metrics import max_position_correlation, turnover_rate


def create_universe():
    """Create a universe of assets with varying performance."""
    np.random.seed(42)
    dates = pd.date_range("2023-01-01", periods=252, freq="D")

    def create_asset(symbol, base_price, drift, volatility):
        """Create a single asset."""
        returns = np.random.normal(drift, volatility, len(dates))
        prices = base_price * np.exp(np.cumsum(returns))

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
            volume=pd.Series(np.random.randint(500000, 3000000, len(dates)), index=dates),
        )

    # Create stocks with different momentum profiles
    return {
        "WINNER1": create_asset("WINNER1", 100, 0.001, 0.02),    # Strong winner
        "WINNER2": create_asset("WINNER2", 80, 0.0008, 0.018),   # Moderate winner
        "NEUTRAL1": create_asset("NEUTRAL1", 50, 0.0002, 0.015), # Neutral
        "NEUTRAL2": create_asset("NEUTRAL2", 60, 0.0001, 0.016), # Neutral
        "LOSER1": create_asset("LOSER1", 120, -0.0005, 0.019),   # Moderate loser
        "LOSER2": create_asset("LOSER2", 90, -0.0008, 0.022),    # Strong loser
    }


def main():
    """Run the long-short strategy example."""
    print("=" * 70)
    print("Long-Short Equity Strategy Example")
    print("=" * 70)

    # Create universe
    print("\n1. Creating universe of 6 stocks...")
    timeseries_data = create_universe()
    print(f"   Created {len(timeseries_data)} stocks with 252 days of data")

    # Define long-short strategy
    print("\n2. Creating long-short strategy...")
    strategy = LongShortStrategy(
        name="Momentum Long-Short",
        symbols=list(timeseries_data.keys()),
        lookback_period=60,     # 60-day momentum
        long_pct=0.33,          # Long top 33% (top 2 stocks)
        short_pct=0.33,         # Short bottom 33% (bottom 2 stocks)
        rebalance_frequency=30, # Monthly rebalance
    )

    print(f"   Strategy: {strategy.name}")
    print(f"   Lookback: {strategy.lookback_period} days")
    print(f"   Long: Top {int(strategy.long_pct * 100)}% of stocks")
    print(f"   Short: Bottom {int(strategy.short_pct * 100)}% of stocks")
    print(f"   Rebalance: Every {strategy.rebalance_frequency} days")

    # Run backtest
    print("\n3. Running backtest...")
    backtest = run_portfolio_backtest(
        strategy=strategy,
        timeseries_data=timeseries_data,
        initial_capital=100000.0,
        commission=0.001,
        slippage=0.001,
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
        calmar = metrics.calmar_ratio(returns)

        print(f"\n   Sharpe Ratio:        {sharpe:.3f}")
        print(f"   Sortino Ratio:       {sortino:.3f}")
        print(f"   Calmar Ratio:        {calmar:.3f}")
        print(f"   Max Drawdown:        {max_dd:.2f}%")

    print(f"\n   Total Trades:        {len(backtest.trades)}")

    if backtest.trades:
        winning_trades = [t for t in backtest.trades if t.pnl > 0]
        losing_trades = [t for t in backtest.trades if t.pnl < 0]
        win_rate_pct = (len(winning_trades) / len(backtest.trades)) * 100 if backtest.trades else 0

        print(f"   Winning Trades:      {len(winning_trades)}")
        print(f"   Losing Trades:       {len(losing_trades)}")
        print(f"   Win Rate:            {win_rate_pct:.1f}%")

        if winning_trades and losing_trades:
            profit_factor = abs(sum(t.pnl for t in winning_trades) / sum(t.pnl for t in losing_trades))
            print(f"   Profit Factor:       {profit_factor:.2f}")

    print("\n" + "=" * 70)
    print("Backtest Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
