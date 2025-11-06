"""
Portfolio Backtest Engine - Event-driven portfolio backtest implementation.

This adapter implements a portfolio backtesting engine that handles multiple
symbols, rebalancing, position sizing, and risk management.
"""

import pandas as pd
import numpy as np
from typing import Dict, List
from canopy.ports.portfolio_backtest_engine import IPortfolioBacktestEngine
from canopy.domain.portfolio_strategy import PortfolioStrategy
from canopy.domain.timeseries import TimeSeries
from canopy.domain.backtest import Backtest, Trade
from canopy.domain.portfolio import Portfolio, Position


class PortfolioBacktestEngine(IPortfolioBacktestEngine):
    """
    Portfolio backtest engine with event-driven execution.

    This engine supports:
    - Multiple symbols
    - Portfolio rebalancing
    - Position sizing
    - Transaction costs (commission + slippage)
    - Risk management
    """

    def run(
        self,
        strategy: PortfolioStrategy,
        timeseries_data: Dict[str, TimeSeries],
        initial_capital: float = 100000.0,
        commission: float = 0.0,
        slippage: float = 0.0,
    ) -> Backtest:
        """
        Run portfolio backtest.

        Args:
            strategy: Portfolio strategy to backtest
            timeseries_data: Dictionary mapping symbol to TimeSeries
            initial_capital: Starting capital
            commission: Commission per trade as percentage
            slippage: Slippage per trade as percentage

        Returns:
            Backtest object with results

        Raises:
            ValueError: If inputs are invalid
        """
        # Validate inputs
        if initial_capital <= 0:
            raise ValueError("Initial capital must be positive")

        if not timeseries_data:
            raise ValueError("Timeseries data must not be empty")

        # Generate signals from strategy
        signals = strategy.generate_signals(timeseries_data)

        if not signals:
            # No signals, return flat equity curve
            first_symbol = list(timeseries_data.keys())[0]
            dates = timeseries_data[first_symbol].close.index
            return Backtest(
                strategy_name=strategy.name,
                initial_capital=initial_capital,
                equity_curve=pd.Series([initial_capital] * len(dates), index=dates),
                trades=[],
            )

        # Get common date range across all symbols
        date_indices = [ts.close.index for ts in timeseries_data.values()]
        common_dates = date_indices[0]
        for idx in date_indices[1:]:
            common_dates = common_dates.intersection(idx)

        common_dates = common_dates.sort_values()

        # Initialize portfolio
        portfolio = Portfolio(
            initial_capital=initial_capital,
            positions={},
            cash=initial_capital,
        )

        # Track equity over time
        equity_series = []
        equity_dates = []

        # Track all trades
        all_trades = []

        # Signal index for tracking
        signal_idx = 0
        current_signal = signals[signal_idx] if signals else None

        # Simulate day by day
        for date in common_dates:
            # Get current prices
            current_prices = {
                symbol: float(ts.close.loc[date])
                for symbol, ts in timeseries_data.items()
                if date in ts.close.index
            }

            # Check if we have a rebalance signal for this date
            while current_signal and current_signal.timestamp <= date:
                # Execute rebalance
                trades = self._rebalance_portfolio(
                    portfolio=portfolio,
                    target_weights=current_signal.target_weights,
                    current_prices=current_prices,
                    timestamp=date,
                    commission=commission,
                    slippage=slippage,
                )
                all_trades.extend(trades)

                # Move to next signal
                signal_idx += 1
                current_signal = signals[signal_idx] if signal_idx < len(signals) else None

            # Record equity
            total_equity = portfolio.total_value(current_prices)
            equity_series.append(total_equity)
            equity_dates.append(date)

        # Create equity curve
        equity_curve = pd.Series(equity_series, index=equity_dates)

        return Backtest(
            strategy_name=strategy.name,
            initial_capital=initial_capital,
            equity_curve=equity_curve,
            trades=all_trades,
        )

    def _rebalance_portfolio(
        self,
        portfolio: Portfolio,
        target_weights: Dict[str, float],
        current_prices: Dict[str, float],
        timestamp: pd.Timestamp,
        commission: float,
        slippage: float,
    ) -> List[Trade]:
        """
        Rebalance portfolio to target weights.

        Args:
            portfolio: Current portfolio
            target_weights: Target weights by symbol
            current_prices: Current prices by symbol
            timestamp: Rebalance timestamp
            commission: Commission rate
            slippage: Slippage rate

        Returns:
            List of trades executed
        """
        trades = []

        # Calculate total portfolio value
        total_value = portfolio.total_value(current_prices)

        if total_value <= 0:
            return trades

        # Calculate target dollar amounts
        target_amounts = {
            symbol: total_value * weight
            for symbol, weight in target_weights.items()
        }

        # Calculate current dollar amounts
        current_amounts = {}
        for symbol, position in portfolio.positions.items():
            if symbol in current_prices:
                current_amounts[symbol] = position.market_value(current_prices[symbol])
            else:
                current_amounts[symbol] = 0.0

        # Add symbols in target but not currently held
        for symbol in target_weights:
            if symbol not in current_amounts:
                current_amounts[symbol] = 0.0

        # Execute trades to reach target weights
        for symbol in set(list(target_weights.keys()) + list(current_amounts.keys())):
            target = target_amounts.get(symbol, 0.0)
            current = current_amounts.get(symbol, 0.0)
            difference = target - current

            if symbol not in current_prices:
                continue

            price = current_prices[symbol]

            # Close position if target is zero and we currently hold it
            if abs(target) < 1.0 and symbol in portfolio.positions:
                trade = self._close_position(
                    portfolio=portfolio,
                    symbol=symbol,
                    price=price,
                    timestamp=timestamp,
                    commission=commission,
                    slippage=slippage,
                )
                if trade:
                    trades.append(trade)

            # Open or adjust position
            elif abs(difference) > 1.0:  # Only trade if difference > $1
                if symbol in portfolio.positions:
                    # Adjust existing position
                    old_position = portfolio.positions[symbol]
                    new_quantity = target / price

                    if new_quantity > old_position.quantity:
                        # Add to position
                        quantity_to_add = new_quantity - old_position.quantity
                        cost = quantity_to_add * price * (1 + commission + slippage)

                        if cost <= portfolio.cash:
                            portfolio.cash -= cost
                            # Update position (simplified - just tracking last entry)
                            portfolio.positions[symbol] = Position(
                                symbol=symbol,
                                quantity=new_quantity,
                                entry_price=price,
                                entry_time=timestamp,
                            )
                    else:
                        # Reduce position (partial close)
                        quantity_to_sell = old_position.quantity - new_quantity
                        proceeds = quantity_to_sell * price * (1 - commission - slippage)
                        portfolio.cash += proceeds

                        if new_quantity > 0:
                            portfolio.positions[symbol] = Position(
                                symbol=symbol,
                                quantity=new_quantity,
                                entry_price=old_position.entry_price,
                                entry_time=old_position.entry_time,
                            )
                        else:
                            del portfolio.positions[symbol]

                        # Create trade record
                        pnl = (price - old_position.entry_price) * quantity_to_sell
                        trades.append(
                            Trade(
                                entry_time=old_position.entry_time,
                                exit_time=timestamp,
                                entry_price=old_position.entry_price,
                                exit_price=price,
                                quantity=quantity_to_sell,
                                side="long",
                                pnl=float(pnl),
                                return_pct=float((price - old_position.entry_price) / old_position.entry_price * 100),
                            )
                        )

                else:
                    # Open new position
                    quantity = target / price
                    cost = target * (1 + commission + slippage)

                    if cost <= portfolio.cash:
                        position = Position(
                            symbol=symbol,
                            quantity=quantity,
                            entry_price=price,
                            entry_time=timestamp,
                        )
                        portfolio.positions[symbol] = position
                        portfolio.cash -= cost

        return trades

    def _close_position(
        self,
        portfolio: Portfolio,
        symbol: str,
        price: float,
        timestamp: pd.Timestamp,
        commission: float,
        slippage: float,
    ) -> Trade:
        """
        Close a position.

        Args:
            portfolio: Portfolio
            symbol: Symbol to close
            price: Exit price
            timestamp: Exit timestamp
            commission: Commission rate
            slippage: Slippage rate

        Returns:
            Trade object
        """
        if symbol not in portfolio.positions:
            return None

        position = portfolio.positions[symbol]

        # Calculate proceeds
        gross_proceeds = position.quantity * price
        net_proceeds = gross_proceeds * (1 - commission - slippage)
        portfolio.cash += net_proceeds

        # Calculate P&L
        cost_basis = position.quantity * position.entry_price
        pnl = net_proceeds - cost_basis

        # Remove position
        del portfolio.positions[symbol]

        # Create trade record
        return Trade(
            entry_time=position.entry_time,
            exit_time=timestamp,
            entry_price=position.entry_price,
            exit_price=price,
            quantity=position.quantity,
            side="long",
            pnl=float(pnl),
            return_pct=float((price - position.entry_price) / position.entry_price * 100),
        )
