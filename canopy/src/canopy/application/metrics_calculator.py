"""Metrics calculator for backtest results"""

import numpy as np
from canopy.domain.backtest import Backtest


class BacktestMetrics:
    """Backtest performance metrics"""

    def __init__(self, backtest: Backtest):
        """
        Initialize metrics from backtest results

        Args:
            backtest: Backtest results
        """
        self.backtest = backtest
        self._calculate_metrics()

    def _calculate_metrics(self) -> None:
        """Calculate all metrics"""
        trades = self.backtest.trades

        # Total return
        self.total_return = self.backtest.total_return()

        if not trades:
            # No trades executed
            self.sharpe_ratio = 0.0
            self.sortino_ratio = 0.0
            self.max_drawdown = 0.0
            self.win_rate = 0.0
            self.profit_factor = 0.0
            self.total_trades = 0
            self.winning_trades = 0
            self.losing_trades = 0
            return

        # Win rate
        self.winning_trades = sum(1 for t in trades if t.pnl > 0)
        self.losing_trades = len(trades) - self.winning_trades
        self.total_trades = len(trades)
        self.win_rate = (self.winning_trades / self.total_trades) * 100 if trades else 0

        # Profit factor
        total_profit = sum(t.pnl for t in trades if t.pnl > 0)
        total_loss = abs(sum(t.pnl for t in trades if t.pnl < 0))
        self.profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')

        # Returns for each trade
        returns = [t.return_pct / 100 for t in trades]

        # Sharpe ratio (simplified)
        if len(returns) > 1:
            mean_return = np.mean(returns)
            std_return = np.std(returns)
            self.sharpe_ratio = (mean_return / std_return) * np.sqrt(252) if std_return > 0 else 0
        else:
            self.sharpe_ratio = 0

        # Sortino ratio (simplified)
        negative_returns = [r for r in returns if r < 0]
        if negative_returns:
            downside_std = np.std(negative_returns)
            self.sortino_ratio = (np.mean(returns) / downside_std) * np.sqrt(252) if downside_std > 0 else 0
        else:
            self.sortino_ratio = self.sharpe_ratio

        # Max drawdown
        equity_curve = self.backtest.equity_curve
        peak = equity_curve.iloc[0]
        max_dd = 0
        for value in equity_curve:
            if value > peak:
                peak = value
            drawdown = ((peak - value) / peak) * 100
            if drawdown > max_dd:
                max_dd = drawdown
        self.max_drawdown = max_dd
