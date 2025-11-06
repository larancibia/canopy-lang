"""
Simple Backtest Engine - Vectorized backtest implementation.

This adapter implements a simple, vectorized backtesting engine following
hexagonal architecture principles.
"""

import pandas as pd
import numpy as np
from typing import List
from canopy.ports.backtest_engine import IBacktestEngine
from canopy.domain.strategy import Strategy
from canopy.domain.timeseries import TimeSeries
from canopy.domain.backtest import Backtest, Trade
from canopy.domain.signal import SignalType


class SimpleBacktestEngine(IBacktestEngine):
    """
    Simple vectorized backtest engine.

    This engine implements a basic long-only backtesting approach:
    1. Generate signals from the strategy
    2. Create positions (1 = long, 0 = flat)
    3. Calculate returns
    4. Apply commissions and slippage
    5. Calculate equity curve
    6. Extract trades
    """

    def run(
        self,
        strategy: Strategy,
        timeseries: TimeSeries,
        initial_capital: float = 10000.0,
        commission: float = 0.0,
        slippage: float = 0.0
    ) -> Backtest:
        """
        Run backtest using vectorized approach.

        Steps:
        1. Generate signals from strategy
        2. Calculate positions (1 = long, 0 = flat)
        3. Calculate returns
        4. Apply commissions and slippage
        5. Calculate equity curve
        6. Extract trades
        7. Return Backtest object

        Args:
            strategy: Strategy to backtest
            timeseries: Historical OHLCV data
            initial_capital: Starting capital
            commission: Commission per trade as percentage
            slippage: Slippage per trade as percentage

        Returns:
            Backtest object with results
        """
        # Validate inputs
        if initial_capital <= 0:
            raise ValueError("Initial capital must be positive")

        if len(timeseries) == 0:
            raise ValueError("Timeseries must not be empty")

        # 1. Generate signals from strategy
        signals = strategy.generate_signals(timeseries)

        # 2. Create position series (1 = long, 0 = flat)
        positions = self._signals_to_positions(signals, timeseries)

        # 3. Calculate returns
        close_prices = timeseries.close
        returns = close_prices.pct_change()

        # 4. Calculate strategy returns (position * market return)
        strategy_returns = positions.shift(1) * returns  # Shift to avoid look-ahead bias
        strategy_returns = strategy_returns.fillna(0.0)

        # 5. Apply costs (commission + slippage) on position changes
        position_changes = positions.diff().fillna(0.0)
        costs = position_changes.abs() * (commission + slippage)
        strategy_returns -= costs

        # 6. Calculate equity curve
        equity_curve = initial_capital * (1 + strategy_returns).cumprod()
        equity_curve.iloc[0] = initial_capital  # Ensure first value is initial capital

        # 7. Extract trades
        trades = self._extract_trades(
            positions, close_prices, equity_curve, initial_capital, commission, slippage
        )

        # 8. Return Backtest object
        return Backtest(
            strategy_name=strategy.name,
            initial_capital=initial_capital,
            equity_curve=equity_curve,
            trades=trades
        )

    def _signals_to_positions(
        self, signals: List, timeseries: TimeSeries
    ) -> pd.Series:
        """
        Convert signals to position series.

        Args:
            signals: List of Signal objects
            timeseries: Time series data

        Returns:
            Series where 1 = long position, 0 = flat
        """
        # Start with all zeros (no position)
        positions = pd.Series(0.0, index=timeseries.close.index)

        if len(signals) == 0:
            return positions

        # Track current position
        in_position = False

        for signal in signals:
            # Find the index for this signal's timestamp
            signal_idx = timeseries.close.index.get_indexer([signal.timestamp], method='nearest')[0]

            if signal.type == SignalType.BUY and not in_position:
                # Enter long position
                positions.iloc[signal_idx:] = 1.0
                in_position = True
            elif signal.type == SignalType.SELL and in_position:
                # Exit position
                positions.iloc[signal_idx:] = 0.0
                in_position = False

        return positions

    def _extract_trades(
        self,
        positions: pd.Series,
        prices: pd.Series,
        equity_curve: pd.Series,
        initial_capital: float,
        commission: float,
        slippage: float
    ) -> List[Trade]:
        """
        Extract individual trades from position series.

        Args:
            positions: Position series (1 = long, 0 = flat)
            prices: Close prices
            equity_curve: Equity curve
            initial_capital: Initial capital
            commission: Commission percentage
            slippage: Slippage percentage

        Returns:
            List of Trade objects
        """
        trades = []

        # Find position changes
        position_changes = positions.diff()

        entry_idx = None
        entry_price = None
        entry_equity = initial_capital

        for i in range(len(position_changes)):
            if position_changes.iloc[i] > 0:
                # Entry signal
                entry_idx = i
                entry_price = prices.iloc[i]
                entry_equity = equity_curve.iloc[i - 1] if i > 0 else initial_capital

            elif position_changes.iloc[i] < 0 and entry_idx is not None:
                # Exit signal
                exit_idx = i
                exit_price = prices.iloc[i]
                exit_equity = equity_curve.iloc[i]

                # Calculate trade metrics
                raw_return = (exit_price - entry_price) / entry_price
                # Apply costs
                total_costs = 2 * (commission + slippage)  # Entry + exit
                net_return = raw_return - total_costs

                # Calculate P&L
                pnl = entry_equity * net_return

                # Create trade object
                trade = Trade(
                    entry_time=pd.Timestamp(prices.index[entry_idx]),
                    exit_time=pd.Timestamp(prices.index[exit_idx]),
                    entry_price=float(entry_price),
                    exit_price=float(exit_price),
                    quantity=entry_equity / entry_price,  # Number of shares
                    side="long",
                    pnl=float(pnl),
                    return_pct=float(net_return * 100.0)
                )
                trades.append(trade)

                # Reset for next trade
                entry_idx = None
                entry_price = None

        return trades
