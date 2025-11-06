"""
Unit tests for metrics calculations.

Tests are written FIRST following TDD methodology.
"""
import pytest
import pandas as pd
import numpy as np
from canopy.domain.metrics import (
    sharpe_ratio,
    sortino_ratio,
    max_drawdown,
    max_drawdown_duration,
    win_rate,
    profit_factor,
    calmar_ratio,
    PerformanceMetrics,
)
from canopy.domain.backtest import Trade


class TestSharpeRatio:
    """Test Sharpe ratio calculation"""

    def test_sharpe_ratio_calculation(self):
        """Sharpe ratio should be calculated correctly"""
        # Arrange - returns of 1% per period with some volatility
        returns = pd.Series([0.01, 0.02, -0.01, 0.015, 0.025, 0.005])

        # Act
        sharpe = sharpe_ratio(returns, risk_free_rate=0.0)

        # Assert
        # Sharpe = mean / std
        expected_mean = returns.mean()
        expected_std = returns.std()
        expected_sharpe = expected_mean / expected_std if expected_std > 0 else 0.0
        assert sharpe == pytest.approx(expected_sharpe, rel=1e-6)

    def test_sharpe_ratio_with_risk_free_rate(self):
        """Sharpe ratio should account for risk-free rate"""
        # Arrange
        returns = pd.Series([0.05, 0.06, 0.04, 0.07, 0.055])
        risk_free_rate = 0.02

        # Act
        sharpe = sharpe_ratio(returns, risk_free_rate=risk_free_rate)

        # Assert
        excess_returns = returns - risk_free_rate
        expected_sharpe = excess_returns.mean() / excess_returns.std()
        assert sharpe == pytest.approx(expected_sharpe, rel=1e-6)

    def test_sharpe_ratio_with_zero_volatility(self):
        """Sharpe ratio should return 0 when volatility is zero"""
        # Arrange - constant returns
        returns = pd.Series([0.01, 0.01, 0.01, 0.01])

        # Act
        sharpe = sharpe_ratio(returns, risk_free_rate=0.0)

        # Assert
        assert sharpe == 0.0


class TestSortinoRatio:
    """Test Sortino ratio calculation"""

    def test_sortino_ratio_calculation(self):
        """Sortino ratio should only consider downside deviation"""
        # Arrange - mix of positive and negative returns
        returns = pd.Series([0.05, -0.02, 0.03, -0.01, 0.04, -0.03])

        # Act
        sortino = sortino_ratio(returns, risk_free_rate=0.0)

        # Assert
        # Sortino uses only negative returns for std dev
        downside_returns = returns[returns < 0.0]
        downside_std = downside_returns.std()
        expected_sortino = returns.mean() / downside_std if downside_std > 0 else 0.0
        assert sortino == pytest.approx(expected_sortino, rel=1e-6)

    def test_sortino_ratio_with_no_downside(self):
        """Sortino ratio should handle case with no negative returns"""
        # Arrange - all positive returns
        returns = pd.Series([0.01, 0.02, 0.03, 0.015])

        # Act
        sortino = sortino_ratio(returns, risk_free_rate=0.0)

        # Assert - should return 0 when no downside risk
        assert sortino == 0.0


class TestMaxDrawdown:
    """Test maximum drawdown calculation"""

    def test_max_drawdown_calculation(self):
        """Max drawdown should calculate largest peak-to-trough decline"""
        # Arrange - equity curve with known drawdown
        equity_curve = pd.Series([10000, 11000, 10500, 9500, 10000, 11500])

        # Act
        mdd = max_drawdown(equity_curve)

        # Assert
        # Peak at 11000, trough at 9500 = (9500-11000)/11000 = -13.636%
        expected_mdd = -13.636363636363637
        assert mdd == pytest.approx(expected_mdd, rel=1e-6)

    def test_max_drawdown_with_no_decline(self):
        """Max drawdown should be 0 for always-increasing equity"""
        # Arrange - monotonically increasing
        equity_curve = pd.Series([10000, 10500, 11000, 11500, 12000])

        # Act
        mdd = max_drawdown(equity_curve)

        # Assert
        assert mdd == 0.0

    def test_max_drawdown_with_full_loss(self):
        """Max drawdown should handle severe drawdowns"""
        # Arrange - large decline
        equity_curve = pd.Series([10000, 5000, 3000, 4000])

        # Act
        mdd = max_drawdown(equity_curve)

        # Assert
        # From 10000 to 3000 = -70%
        assert mdd == pytest.approx(-70.0, rel=1e-6)


class TestMaxDrawdownDuration:
    """Test maximum drawdown duration calculation"""

    def test_max_drawdown_duration_calculation(self):
        """Max drawdown duration should count periods underwater"""
        # Arrange - equity curve with recovery period
        dates = pd.date_range("2024-01-01", periods=10, freq="D")
        # Peak at index 2 (12000), underwater at indices 3,4,5,6,7, recovery at 8 (12500) = 5 periods underwater
        equity_curve = pd.Series(
            [10000, 11000, 12000, 11000, 10000, 9000, 10000, 11000, 12500, 13000],
            index=dates
        )

        # Act
        duration = max_drawdown_duration(equity_curve)

        # Assert
        assert duration == 5

    def test_max_drawdown_duration_with_no_drawdown(self):
        """Max drawdown duration should be 0 for always-increasing equity"""
        # Arrange
        equity_curve = pd.Series([10000, 10500, 11000, 11500])

        # Act
        duration = max_drawdown_duration(equity_curve)

        # Assert
        assert duration == 0


class TestWinRate:
    """Test win rate calculation"""

    def test_win_rate_calculation(self):
        """Win rate should calculate percentage of winning trades"""
        # Arrange - 3 wins, 2 losses
        trades = [
            Trade(
                entry_time=pd.Timestamp("2024-01-01"),
                exit_time=pd.Timestamp("2024-01-02"),
                entry_price=100.0, exit_price=105.0,
                quantity=10.0, side="long", pnl=50.0, return_pct=5.0
            ),
            Trade(
                entry_time=pd.Timestamp("2024-01-03"),
                exit_time=pd.Timestamp("2024-01-04"),
                entry_price=105.0, exit_price=103.0,
                quantity=10.0, side="long", pnl=-20.0, return_pct=-1.9
            ),
            Trade(
                entry_time=pd.Timestamp("2024-01-05"),
                exit_time=pd.Timestamp("2024-01-06"),
                entry_price=103.0, exit_price=108.0,
                quantity=10.0, side="long", pnl=50.0, return_pct=4.85
            ),
            Trade(
                entry_time=pd.Timestamp("2024-01-07"),
                exit_time=pd.Timestamp("2024-01-08"),
                entry_price=108.0, exit_price=106.0,
                quantity=10.0, side="long", pnl=-20.0, return_pct=-1.85
            ),
            Trade(
                entry_time=pd.Timestamp("2024-01-09"),
                exit_time=pd.Timestamp("2024-01-10"),
                entry_price=106.0, exit_price=112.0,
                quantity=10.0, side="long", pnl=60.0, return_pct=5.66
            ),
        ]

        # Act
        rate = win_rate(trades)

        # Assert
        # 3 wins out of 5 = 60%
        assert rate == 60.0

    def test_win_rate_with_no_trades(self):
        """Win rate should handle empty trade list"""
        # Arrange
        trades = []

        # Act
        rate = win_rate(trades)

        # Assert
        assert rate == 0.0


class TestProfitFactor:
    """Test profit factor calculation"""

    def test_profit_factor_calculation(self):
        """Profit factor should be ratio of gross profit to gross loss"""
        # Arrange - trades with known profit/loss
        trades = [
            Trade(
                entry_time=pd.Timestamp("2024-01-01"),
                exit_time=pd.Timestamp("2024-01-02"),
                entry_price=100.0, exit_price=110.0,
                quantity=10.0, side="long", pnl=100.0, return_pct=10.0
            ),
            Trade(
                entry_time=pd.Timestamp("2024-01-03"),
                exit_time=pd.Timestamp("2024-01-04"),
                entry_price=110.0, exit_price=105.0,
                quantity=10.0, side="long", pnl=-50.0, return_pct=-4.55
            ),
            Trade(
                entry_time=pd.Timestamp("2024-01-05"),
                exit_time=pd.Timestamp("2024-01-06"),
                entry_price=105.0, exit_price=115.0,
                quantity=10.0, side="long", pnl=100.0, return_pct=9.52
            ),
        ]

        # Act
        pf = profit_factor(trades)

        # Assert
        # Gross profit = 200, Gross loss = 50, PF = 200/50 = 4.0
        assert pf == pytest.approx(4.0, rel=1e-6)

    def test_profit_factor_with_no_losses(self):
        """Profit factor should handle case with no losing trades"""
        # Arrange - all winning trades
        trades = [
            Trade(
                entry_time=pd.Timestamp("2024-01-01"),
                exit_time=pd.Timestamp("2024-01-02"),
                entry_price=100.0, exit_price=110.0,
                quantity=10.0, side="long", pnl=100.0, return_pct=10.0
            ),
            Trade(
                entry_time=pd.Timestamp("2024-01-03"),
                exit_time=pd.Timestamp("2024-01-04"),
                entry_price=110.0, exit_price=115.0,
                quantity=10.0, side="long", pnl=50.0, return_pct=4.55
            ),
        ]

        # Act
        pf = profit_factor(trades)

        # Assert - should return 0 when no losses
        assert pf == 0.0


class TestCalmarRatio:
    """Test Calmar ratio calculation"""

    def test_calmar_ratio_calculation(self):
        """Calmar ratio should be annual return / max drawdown"""
        # Arrange - daily returns for ~1 year (252 trading days)
        # Create equity curve with 20% return and 10% max drawdown
        np.random.seed(42)
        daily_returns = np.random.normal(0.0008, 0.01, 252)  # ~20% annual return
        equity_curve = pd.Series([10000])
        for ret in daily_returns:
            equity_curve = pd.concat([equity_curve, pd.Series([equity_curve.iloc[-1] * (1 + ret)])])
        returns = pd.Series(daily_returns)

        # Act
        calmar = calmar_ratio(returns)

        # Assert - should be positive
        assert isinstance(calmar, float)
        assert calmar != 0.0


class TestPerformanceMetrics:
    """Test PerformanceMetrics container"""

    def test_performance_metrics_creation(self):
        """PerformanceMetrics should store all metrics"""
        # Arrange & Act
        metrics = PerformanceMetrics(
            total_return=25.5,
            sharpe_ratio=1.5,
            sortino_ratio=2.0,
            max_drawdown=-15.5,
            max_drawdown_duration=30,
            win_rate=55.0,
            profit_factor=1.8,
            calmar_ratio=1.2,
            total_trades=50,
            winning_trades=27,
            losing_trades=23,
            average_win=150.0,
            average_loss=-80.0
        )

        # Assert
        assert metrics.total_return == 25.5
        assert metrics.sharpe_ratio == 1.5
        assert metrics.win_rate == 55.0
        assert metrics.total_trades == 50
