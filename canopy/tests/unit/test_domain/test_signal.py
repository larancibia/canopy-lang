"""Tests for Signal domain entities"""

import pytest
import pandas as pd
from datetime import datetime

from canopy.domain.signal import Signal, SignalType, crossover, crossunder


class TestSignalType:
    """Test suite for SignalType enum"""

    def test_signal_type_buy(self) -> None:
        """Test BUY signal type"""
        assert SignalType.BUY.value == "BUY"

    def test_signal_type_sell(self) -> None:
        """Test SELL signal type"""
        assert SignalType.SELL.value == "SELL"


class TestSignal:
    """Test suite for Signal"""

    def test_signal_buy_creation(self) -> None:
        """Test creating a BUY signal"""
        signal = Signal(
            type=SignalType.BUY,
            timestamp=datetime(2024, 1, 1, 10, 0, 0),
            price=100.0,
            reason="Test buy signal",
        )

        assert signal.type == SignalType.BUY
        assert signal.timestamp == datetime(2024, 1, 1, 10, 0, 0)
        assert signal.price == 100.0
        assert signal.reason == "Test buy signal"

    def test_signal_sell_creation(self) -> None:
        """Test creating a SELL signal"""
        signal = Signal(
            type=SignalType.SELL,
            timestamp=datetime(2024, 1, 2, 15, 30, 0),
            price=105.0,
            reason="Test sell signal",
        )

        assert signal.type == SignalType.SELL
        assert signal.timestamp == datetime(2024, 1, 2, 15, 30, 0)
        assert signal.price == 105.0
        assert signal.reason == "Test sell signal"

    def test_signal_without_reason(self) -> None:
        """Test creating a signal without a reason"""
        signal = Signal(
            type=SignalType.BUY,
            timestamp=datetime(2024, 1, 1, 10, 0, 0),
            price=100.0,
        )

        assert signal.type == SignalType.BUY
        assert signal.reason is None

    def test_signal_str_representation(self) -> None:
        """Test string representation of signal"""
        signal = Signal(
            type=SignalType.BUY,
            timestamp=datetime(2024, 1, 1, 10, 0, 0),
            price=100.50,
            reason="Test",
        )

        str_repr = str(signal)
        assert "BUY" in str_repr
        assert "100.50" in str_repr


class TestCrossover:
    """Test suite for crossover detection"""

    def test_crossover_detection(self) -> None:
        """Test detecting when series1 crosses above series2"""
        dates = pd.date_range(start="2024-01-01", periods=10, freq="D")

        # Series1 starts below, crosses above at index 5
        series1 = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], index=dates)
        series2 = pd.Series([6, 6, 6, 6, 6, 5, 5, 5, 5, 5], index=dates)

        result = crossover(series1, series2)

        assert isinstance(result, pd.Series)
        assert len(result) == len(series1)

        # Crossover should occur at index 5 (when series1 goes from 5 to 6 and series2 is at 5)
        assert result.iloc[5] == True
        # All other values should be False
        assert result.iloc[:5].sum() == 0
        assert result.iloc[6:].sum() == 0

    def test_crossover_no_cross(self) -> None:
        """Test when there is no crossover"""
        dates = pd.date_range(start="2024-01-01", periods=10, freq="D")

        # Series1 always below series2
        series1 = pd.Series([1, 2, 3, 4, 5, 4, 3, 2, 1, 2], index=dates)
        series2 = pd.Series([6, 6, 6, 6, 6, 6, 6, 6, 6, 6], index=dates)

        result = crossover(series1, series2)

        # No crossovers should occur
        assert result.sum() == 0
        assert (result == False).all()

    def test_crossover_multiple(self) -> None:
        """Test detecting multiple crossovers"""
        dates = pd.date_range(start="2024-01-01", periods=10, freq="D")

        # Multiple crossovers
        series1 = pd.Series([1, 6, 1, 6, 1, 6, 1, 6, 1, 6], index=dates)
        series2 = pd.Series([5, 5, 5, 5, 5, 5, 5, 5, 5, 5], index=dates)

        result = crossover(series1, series2)

        # Should detect crossovers at indices 1, 3, 5, 7, 9
        crossover_count = result.sum()
        assert crossover_count == 5

    def test_crossover_equal_values(self) -> None:
        """Test when series are equal (no crossover)"""
        dates = pd.date_range(start="2024-01-01", periods=10, freq="D")

        # Series are equal
        series1 = pd.Series([5, 5, 5, 5, 5, 5, 5, 5, 5, 5], index=dates)
        series2 = pd.Series([5, 5, 5, 5, 5, 5, 5, 5, 5, 5], index=dates)

        result = crossover(series1, series2)

        # No crossovers when equal
        assert result.sum() == 0


class TestCrossunder:
    """Test suite for crossunder detection"""

    def test_crossunder_detection(self) -> None:
        """Test detecting when series1 crosses below series2"""
        dates = pd.date_range(start="2024-01-01", periods=10, freq="D")

        # Series1 starts above, crosses below at index 5
        series1 = pd.Series([10, 9, 8, 7, 6, 5, 4, 3, 2, 1], index=dates)
        series2 = pd.Series([5, 5, 5, 5, 5, 6, 6, 6, 6, 6], index=dates)

        result = crossunder(series1, series2)

        assert isinstance(result, pd.Series)
        assert len(result) == len(series1)

        # Crossunder should occur at index 5
        assert result.iloc[5] == True
        # All other values should be False
        assert result.iloc[:5].sum() == 0
        assert result.iloc[6:].sum() == 0

    def test_crossunder_no_cross(self) -> None:
        """Test when there is no crossunder"""
        dates = pd.date_range(start="2024-01-01", periods=10, freq="D")

        # Series1 always above series2
        series1 = pd.Series([10, 9, 10, 9, 10, 9, 10, 9, 10, 9], index=dates)
        series2 = pd.Series([5, 5, 5, 5, 5, 5, 5, 5, 5, 5], index=dates)

        result = crossunder(series1, series2)

        # No crossunders should occur
        assert result.sum() == 0
        assert (result == False).all()

    def test_crossunder_multiple(self) -> None:
        """Test detecting multiple crossunders"""
        dates = pd.date_range(start="2024-01-01", periods=10, freq="D")

        # Multiple crossunders
        series1 = pd.Series([6, 1, 6, 1, 6, 1, 6, 1, 6, 1], index=dates)
        series2 = pd.Series([5, 5, 5, 5, 5, 5, 5, 5, 5, 5], index=dates)

        result = crossunder(series1, series2)

        # Should detect crossunders at indices 1, 3, 5, 7, 9
        crossunder_count = result.sum()
        assert crossunder_count == 5

    def test_crossunder_equal_values(self) -> None:
        """Test when series are equal (no crossunder)"""
        dates = pd.date_range(start="2024-01-01", periods=10, freq="D")

        # Series are equal
        series1 = pd.Series([5, 5, 5, 5, 5, 5, 5, 5, 5, 5], index=dates)
        series2 = pd.Series([5, 5, 5, 5, 5, 5, 5, 5, 5, 5], index=dates)

        result = crossunder(series1, series2)

        # No crossunders when equal
        assert result.sum() == 0


class TestCrossoverCrossunderSymmetry:
    """Test symmetry between crossover and crossunder"""

    def test_crossover_and_crossunder_are_opposite(self) -> None:
        """Test that crossover and crossunder detect opposite movements"""
        dates = pd.date_range(start="2024-01-01", periods=10, freq="D")

        # Oscillating series
        series1 = pd.Series([1, 6, 1, 6, 1, 6, 1, 6, 1, 6], index=dates)
        series2 = pd.Series([5, 5, 5, 5, 5, 5, 5, 5, 5, 5], index=dates)

        crossovers = crossover(series1, series2)
        crossunders = crossunder(series1, series2)

        # They should never occur at the same index
        assert (crossovers & crossunders).sum() == 0

        # Total signals should equal total crossings
        total_signals = crossovers.sum() + crossunders.sum()
        assert total_signals > 0
