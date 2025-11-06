"""
Backtest Service - Business logic for backtest operations.
"""

from datetime import datetime
from typing import Dict, Any, Tuple
from canopy.parser.parser import parse_strategy
from canopy.application.run_backtest import RunBacktestUseCase
from canopy.adapters.engines.simple_engine import SimpleBacktestEngine
from canopy.ports.data_provider import IDataProvider
from canopy.domain.backtest import Backtest
from canopy.domain.metrics import PerformanceMetrics


class BacktestService:
    """Service for handling backtest-related operations."""

    def __init__(self, data_provider: IDataProvider):
        """
        Initialize the backtest service.

        Args:
            data_provider: Data provider instance
        """
        self.data_provider = data_provider
        self.backtest_engine = SimpleBacktestEngine()
        self.use_case = RunBacktestUseCase(self.backtest_engine)

    def run_backtest(
        self,
        strategy_code: str,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        initial_capital: float = 10000.0,
        commission: float = 0.001,
        slippage: float = 0.0,
    ) -> Tuple[Backtest, PerformanceMetrics]:
        """
        Run a backtest synchronously.

        Args:
            strategy_code: Canopy strategy code
            symbol: Trading symbol
            start_date: Start date
            end_date: End date
            initial_capital: Initial capital
            commission: Commission rate
            slippage: Slippage rate

        Returns:
            Tuple of (Backtest, PerformanceMetrics)

        Raises:
            ValueError: If strategy code is invalid
            Exception: If backtest fails
        """
        # Parse strategy
        strategy = parse_strategy(strategy_code)

        # Fetch data
        timeseries = self.data_provider.fetch_ohlcv(symbol, start_date, end_date)

        # Run backtest
        backtest, metrics = self.use_case.execute(
            strategy=strategy,
            timeseries=timeseries,
            initial_capital=initial_capital,
            commission=commission,
            slippage=slippage,
        )

        return backtest, metrics

    def format_backtest_result(
        self,
        job_id: str,
        backtest: Backtest,
        metrics: PerformanceMetrics,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        initial_capital: float,
    ) -> Dict[str, Any]:
        """
        Format backtest results for API response.

        Args:
            job_id: Job identifier
            backtest: Backtest result
            metrics: Performance metrics
            symbol: Trading symbol
            start_date: Start date
            end_date: End date
            initial_capital: Initial capital

        Returns:
            Dictionary with formatted results
        """
        # Format trades
        trades = []
        for trade in backtest.trades:
            trades.append(
                {
                    "entry_date": trade.entry_date.isoformat(),
                    "exit_date": trade.exit_date.isoformat(),
                    "entry_price": float(trade.entry_price),
                    "exit_price": float(trade.exit_price),
                    "shares": float(trade.shares),
                    "pnl": float(trade.pnl),
                    "return_pct": float(trade.return_pct),
                }
            )

        # Format signals
        signals = []
        for signal in backtest.signals:
            signals.append(
                {
                    "type": signal.type.value,
                    "timestamp": signal.timestamp.isoformat(),
                    "price": float(signal.price),
                    "reason": signal.reason,
                }
            )

        # Format equity curve
        equity_curve = []
        for timestamp, value in backtest.equity_curve.items():
            equity_curve.append({"timestamp": timestamp.isoformat(), "value": float(value)})

        # Format metrics
        metrics_dict = {
            "total_return": float(metrics.total_return),
            "sharpe_ratio": float(metrics.sharpe_ratio),
            "sortino_ratio": float(metrics.sortino_ratio),
            "max_drawdown": float(metrics.max_drawdown),
            "max_drawdown_duration": int(metrics.max_drawdown_duration),
            "win_rate": float(metrics.win_rate),
            "profit_factor": float(metrics.profit_factor),
            "calmar_ratio": float(metrics.calmar_ratio),
            "total_trades": int(metrics.total_trades),
            "winning_trades": int(metrics.winning_trades),
            "losing_trades": int(metrics.losing_trades),
            "average_win": float(metrics.average_win),
            "average_loss": float(metrics.average_loss),
        }

        return {
            "job_id": job_id,
            "status": "completed",
            "strategy_name": backtest.strategy.name,
            "symbol": symbol,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "initial_capital": float(initial_capital),
            "final_capital": float(backtest.final_capital()),
            "metrics": metrics_dict,
            "trades": trades,
            "signals": signals,
            "equity_curve": equity_curve,
            "completed_at": datetime.utcnow().isoformat(),
        }
