"""
Unit tests for portfolio domain models.

Tests for Portfolio, Position, PositionSizer, and Rebalancer classes.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from canopy.domain.portfolio import (
    Position,
    Portfolio,
    PositionSizer,
    EqualWeightSizer,
    RiskParitySizer,
    KellyCriterionSizer,
    Rebalancer,
    PeriodicRebalancer,
)


class TestPosition:
    """Test Position domain model."""

    def test_position_creation(self):
        """Test creating a position."""
        position = Position(
            symbol="AAPL",
            quantity=100.0,
            entry_price=150.0,
            entry_time=pd.Timestamp("2024-01-01"),
        )

        assert position.symbol == "AAPL"
        assert position.quantity == 100.0
        assert position.entry_price == 150.0
        assert position.entry_time == pd.Timestamp("2024-01-01")

    def test_position_market_value(self):
        """Test calculating position market value."""
        position = Position(
            symbol="AAPL",
            quantity=100.0,
            entry_price=150.0,
            entry_time=pd.Timestamp("2024-01-01"),
        )

        market_value = position.market_value(current_price=160.0)
        assert market_value == 16000.0

    def test_position_pnl(self):
        """Test calculating position P&L."""
        position = Position(
            symbol="AAPL",
            quantity=100.0,
            entry_price=150.0,
            entry_time=pd.Timestamp("2024-01-01"),
        )

        pnl = position.pnl(current_price=160.0)
        assert pnl == 1000.0  # (160 - 150) * 100

    def test_position_pnl_negative(self):
        """Test calculating negative position P&L."""
        position = Position(
            symbol="AAPL",
            quantity=100.0,
            entry_price=150.0,
            entry_time=pd.Timestamp("2024-01-01"),
        )

        pnl = position.pnl(current_price=140.0)
        assert pnl == -1000.0  # (140 - 150) * 100

    def test_position_return_pct(self):
        """Test calculating position return percentage."""
        position = Position(
            symbol="AAPL",
            quantity=100.0,
            entry_price=150.0,
            entry_time=pd.Timestamp("2024-01-01"),
        )

        return_pct = position.return_pct(current_price=165.0)
        assert abs(return_pct - 10.0) < 0.01  # (165 - 150) / 150 * 100


class TestPortfolio:
    """Test Portfolio domain model."""

    def test_portfolio_creation(self):
        """Test creating a portfolio."""
        portfolio = Portfolio(
            initial_capital=100000.0,
            positions={},
            cash=100000.0,
        )

        assert portfolio.initial_capital == 100000.0
        assert portfolio.cash == 100000.0
        assert len(portfolio.positions) == 0

    def test_portfolio_add_position(self):
        """Test adding a position to portfolio."""
        portfolio = Portfolio(
            initial_capital=100000.0,
            positions={},
            cash=100000.0,
        )

        position = Position(
            symbol="AAPL",
            quantity=100.0,
            entry_price=150.0,
            entry_time=pd.Timestamp("2024-01-01"),
        )

        portfolio.add_position(position)

        assert "AAPL" in portfolio.positions
        assert portfolio.positions["AAPL"] == position
        assert portfolio.cash == 85000.0  # 100000 - (100 * 150)

    def test_portfolio_remove_position(self):
        """Test removing a position from portfolio."""
        portfolio = Portfolio(
            initial_capital=100000.0,
            positions={},
            cash=85000.0,
        )

        position = Position(
            symbol="AAPL",
            quantity=100.0,
            entry_price=150.0,
            entry_time=pd.Timestamp("2024-01-01"),
        )

        portfolio.positions["AAPL"] = position
        portfolio.remove_position("AAPL", exit_price=160.0)

        assert "AAPL" not in portfolio.positions
        assert portfolio.cash == 101000.0  # 85000 + (100 * 160)

    def test_portfolio_total_value(self):
        """Test calculating total portfolio value."""
        portfolio = Portfolio(
            initial_capital=100000.0,
            positions={},
            cash=70000.0,
        )

        portfolio.positions["AAPL"] = Position(
            symbol="AAPL",
            quantity=100.0,
            entry_price=150.0,
            entry_time=pd.Timestamp("2024-01-01"),
        )

        portfolio.positions["GOOGL"] = Position(
            symbol="GOOGL",
            quantity=50.0,
            entry_price=200.0,
            entry_time=pd.Timestamp("2024-01-01"),
        )

        current_prices = {"AAPL": 160.0, "GOOGL": 210.0}
        total_value = portfolio.total_value(current_prices)

        # 70000 (cash) + 16000 (AAPL: 100 * 160) + 10500 (GOOGL: 50 * 210)
        assert total_value == 96500.0

    def test_portfolio_total_pnl(self):
        """Test calculating total portfolio P&L."""
        portfolio = Portfolio(
            initial_capital=100000.0,
            positions={},
            cash=70000.0,
        )

        portfolio.positions["AAPL"] = Position(
            symbol="AAPL",
            quantity=100.0,
            entry_price=150.0,
            entry_time=pd.Timestamp("2024-01-01"),
        )

        portfolio.positions["GOOGL"] = Position(
            symbol="GOOGL",
            quantity=50.0,
            entry_price=200.0,
            entry_time=pd.Timestamp("2024-01-01"),
        )

        current_prices = {"AAPL": 160.0, "GOOGL": 210.0}
        total_pnl = portfolio.total_pnl(current_prices)

        # AAPL: (160 - 150) * 100 = 1000
        # GOOGL: (210 - 200) * 50 = 500
        # Total: 1500
        assert total_pnl == 1500.0


class TestEqualWeightSizer:
    """Test EqualWeightSizer."""

    def test_equal_weight_sizing(self):
        """Test equal weight position sizing."""
        sizer = EqualWeightSizer(num_positions=4)

        weights = sizer.calculate_weights(
            symbols=["AAPL", "GOOGL", "MSFT", "AMZN"],
            prices={"AAPL": 150.0, "GOOGL": 200.0, "MSFT": 300.0, "AMZN": 100.0},
            capital=100000.0,
        )

        # Each should get 25% (0.25)
        assert all(abs(w - 0.25) < 0.01 for w in weights.values())
        assert abs(sum(weights.values()) - 1.0) < 0.01

    def test_equal_weight_sizing_with_returns(self):
        """Test equal weight sizing ignores returns data."""
        sizer = EqualWeightSizer(num_positions=2)

        returns = pd.DataFrame({
            "AAPL": [0.01, 0.02, -0.01],
            "GOOGL": [-0.01, 0.015, 0.02],
        })

        weights = sizer.calculate_weights(
            symbols=["AAPL", "GOOGL"],
            prices={"AAPL": 150.0, "GOOGL": 200.0},
            capital=100000.0,
            returns=returns,
        )

        # Should still be equal weight
        assert abs(weights["AAPL"] - 0.5) < 0.01
        assert abs(weights["GOOGL"] - 0.5) < 0.01


class TestRiskParitySizer:
    """Test RiskParitySizer."""

    def test_risk_parity_sizing(self):
        """Test risk parity position sizing."""
        sizer = RiskParitySizer()

        # Create returns data with different volatilities
        returns = pd.DataFrame({
            "AAPL": [0.01, -0.01, 0.02, -0.015, 0.01],
            "GOOGL": [0.02, -0.02, 0.03, -0.025, 0.015],  # Higher vol
        })

        weights = sizer.calculate_weights(
            symbols=["AAPL", "GOOGL"],
            prices={"AAPL": 150.0, "GOOGL": 200.0},
            capital=100000.0,
            returns=returns,
        )

        # Lower volatility asset should get higher weight
        assert weights["AAPL"] > weights["GOOGL"]
        assert abs(sum(weights.values()) - 1.0) < 0.01


class TestKellyCriterionSizer:
    """Test KellyCriterionSizer."""

    def test_kelly_criterion_sizing(self):
        """Test Kelly criterion position sizing."""
        sizer = KellyCriterionSizer(fraction=0.5)  # Half Kelly

        returns = pd.DataFrame({
            "AAPL": [0.02, 0.01, 0.03, 0.015, 0.02],  # Positive expected return
            "GOOGL": [-0.01, -0.02, 0.01, -0.015, -0.01],  # Negative expected return
        })

        weights = sizer.calculate_weights(
            symbols=["AAPL", "GOOGL"],
            prices={"AAPL": 150.0, "GOOGL": 200.0},
            capital=100000.0,
            returns=returns,
        )

        # Better performing asset should get higher weight
        assert weights["AAPL"] > weights["GOOGL"]
        assert abs(sum(weights.values()) - 1.0) < 0.01


class TestPeriodicRebalancer:
    """Test PeriodicRebalancer."""

    def test_rebalancer_creation(self):
        """Test creating a periodic rebalancer."""
        rebalancer = PeriodicRebalancer(frequency_days=30)
        assert rebalancer.frequency_days == 30

    def test_should_rebalance_first_time(self):
        """Test should rebalance on first call."""
        rebalancer = PeriodicRebalancer(frequency_days=30)
        current_time = pd.Timestamp("2024-01-15")

        assert rebalancer.should_rebalance(current_time, last_rebalance=None)

    def test_should_rebalance_after_period(self):
        """Test should rebalance after period has passed."""
        rebalancer = PeriodicRebalancer(frequency_days=30)

        last_rebalance = pd.Timestamp("2024-01-01")
        current_time = pd.Timestamp("2024-02-05")  # 35 days later

        assert rebalancer.should_rebalance(current_time, last_rebalance)

    def test_should_not_rebalance_before_period(self):
        """Test should not rebalance before period has passed."""
        rebalancer = PeriodicRebalancer(frequency_days=30)

        last_rebalance = pd.Timestamp("2024-01-01")
        current_time = pd.Timestamp("2024-01-20")  # 19 days later

        assert not rebalancer.should_rebalance(current_time, last_rebalance)
