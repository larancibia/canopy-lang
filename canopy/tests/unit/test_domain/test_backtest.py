"""
Unit tests for Backtest domain entity.

Tests are written FIRST following TDD methodology.
"""
import pytest
import pandas as pd
from datetime import datetime
from canopy.domain.backtest import Trade, Backtest


class TestTrade:
    """Test Trade entity"""

    def test_trade_creation_with_valid_data(self):
        """Trade should be created with valid OHLC data"""
        # Arrange & Act
        trade = Trade(
            entry_time=pd.Timestamp("2024-01-01"),
            exit_time=pd.Timestamp("2024-01-05"),
            entry_price=100.0,
            exit_price=110.0,
            quantity=10.0,
            side="long",
            pnl=100.0,
            return_pct=10.0
        )

        # Assert
        assert trade.entry_price == 100.0
        assert trade.exit_price == 110.0
        assert trade.pnl == 100.0
        assert trade.side == "long"

    def test_trade_validates_side(self):
        """Trade should only accept 'long' or 'short' as side"""
        # Valid sides should work
        long_trade = Trade(
            entry_time=pd.Timestamp("2024-01-01"),
            exit_time=pd.Timestamp("2024-01-05"),
            entry_price=100.0,
            exit_price=110.0,
            quantity=10.0,
            side="long",
            pnl=100.0,
            return_pct=10.0
        )
        assert long_trade.side == "long"

        short_trade = Trade(
            entry_time=pd.Timestamp("2024-01-01"),
            exit_time=pd.Timestamp("2024-01-05"),
            entry_price=100.0,
            exit_price=90.0,
            quantity=10.0,
            side="short",
            pnl=100.0,
            return_pct=10.0
        )
        assert short_trade.side == "short"


class TestBacktest:
    """Test Backtest entity"""

    @pytest.fixture
    def sample_equity_curve(self):
        """Sample equity curve for testing"""
        dates = pd.date_range("2024-01-01", periods=5, freq="D")
        return pd.Series([10000, 10100, 10200, 10150, 10300], index=dates)

    @pytest.fixture
    def sample_trades(self):
        """Sample trades for testing"""
        return [
            Trade(
                entry_time=pd.Timestamp("2024-01-01"),
                exit_time=pd.Timestamp("2024-01-02"),
                entry_price=100.0,
                exit_price=101.0,
                quantity=100.0,
                side="long",
                pnl=100.0,
                return_pct=1.0
            ),
            Trade(
                entry_time=pd.Timestamp("2024-01-03"),
                exit_time=pd.Timestamp("2024-01-04"),
                entry_price=102.0,
                exit_price=101.5,
                quantity=100.0,
                side="long",
                pnl=-50.0,
                return_pct=-0.49
            ),
        ]

    def test_backtest_tracks_equity_curve(self, sample_equity_curve, sample_trades):
        """Backtest should track equity curve"""
        # Arrange & Act
        backtest = Backtest(
            strategy_name="Test Strategy",
            initial_capital=10000.0,
            equity_curve=sample_equity_curve,
            trades=sample_trades
        )

        # Assert
        assert len(backtest.equity_curve) == 5
        assert backtest.equity_curve.iloc[0] == 10000
        assert backtest.equity_curve.iloc[-1] == 10300

    def test_backtest_tracks_trades(self, sample_equity_curve, sample_trades):
        """Backtest should track all trades"""
        # Arrange & Act
        backtest = Backtest(
            strategy_name="Test Strategy",
            initial_capital=10000.0,
            equity_curve=sample_equity_curve,
            trades=sample_trades
        )

        # Assert
        assert len(backtest.trades) == 2
        assert backtest.trades[0].pnl == 100.0
        assert backtest.trades[1].pnl == -50.0

    def test_backtest_calculates_returns(self, sample_equity_curve, sample_trades):
        """Backtest should calculate total return percentage"""
        # Arrange
        backtest = Backtest(
            strategy_name="Test Strategy",
            initial_capital=10000.0,
            equity_curve=sample_equity_curve,
            trades=sample_trades
        )

        # Act
        total_return = backtest.total_return()

        # Assert
        # (10300 - 10000) / 10000 = 0.03 = 3%
        assert total_return == pytest.approx(3.0, rel=1e-6)

    def test_backtest_handles_positions(self, sample_equity_curve, sample_trades):
        """Backtest should handle final equity calculation"""
        # Arrange
        backtest = Backtest(
            strategy_name="Test Strategy",
            initial_capital=10000.0,
            equity_curve=sample_equity_curve,
            trades=sample_trades
        )

        # Act
        final_equity = backtest.final_equity()

        # Assert
        assert final_equity == 10300.0

    def test_backtest_validates_initial_capital(self, sample_equity_curve, sample_trades):
        """Backtest should reject non-positive initial capital"""
        # Act & Assert
        with pytest.raises(ValueError, match="Initial capital must be positive"):
            Backtest(
                strategy_name="Test Strategy",
                initial_capital=0.0,
                equity_curve=sample_equity_curve,
                trades=sample_trades
            )

        with pytest.raises(ValueError, match="Initial capital must be positive"):
            Backtest(
                strategy_name="Test Strategy",
                initial_capital=-1000.0,
                equity_curve=sample_equity_curve,
                trades=sample_trades
            )

    def test_backtest_with_empty_trades(self, sample_equity_curve):
        """Backtest should handle case with no trades"""
        # Arrange
        backtest = Backtest(
            strategy_name="Test Strategy",
            initial_capital=10000.0,
            equity_curve=sample_equity_curve,
            trades=[]
        )

        # Act & Assert
        assert len(backtest.trades) == 0
        assert backtest.final_equity() == 10300.0
        assert backtest.total_return() == pytest.approx(3.0, rel=1e-6)
