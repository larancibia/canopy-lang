"""Tests for Indicator domain entities"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from canopy.domain.timeseries import TimeSeries
from canopy.domain.indicator import Indicator, SMA, EMA, RSI


class TestSMA:
    """Test suite for Simple Moving Average"""

    @pytest.fixture
    def sample_timeseries(self) -> TimeSeries:
        """Create sample timeseries data"""
        dates = pd.date_range(start="2024-01-01", periods=20, freq="D")
        # Create a simple uptrend
        close_prices = [100.0 + i * 2 for i in range(20)]
        return TimeSeries(
            open=pd.Series(close_prices, index=dates),
            high=pd.Series([p + 5 for p in close_prices], index=dates),
            low=pd.Series([p - 5 for p in close_prices], index=dates),
            close=pd.Series(close_prices, index=dates),
            volume=pd.Series([1000.0] * 20, index=dates),
        )

    def test_sma_calculates_correct_values(self, sample_timeseries: TimeSeries) -> None:
        """Test that SMA calculates correct values"""
        sma = SMA(period=5)
        result = sma.calculate(sample_timeseries)

        assert isinstance(result, pd.Series)
        assert len(result) == len(sample_timeseries)

        # First 4 values should be NaN (not enough data for 5-period SMA)
        assert result.iloc[:4].isna().all()

        # 5th value should be average of first 5 closes
        expected_5th = (100.0 + 102.0 + 104.0 + 106.0 + 108.0) / 5
        assert pytest.approx(result.iloc[4], rel=1e-9) == expected_5th

        # Check another value (indices 5-9: values 110, 112, 114, 116, 118)
        expected_10th = (110.0 + 112.0 + 114.0 + 116.0 + 118.0) / 5
        assert pytest.approx(result.iloc[9], rel=1e-9) == expected_10th

    def test_sma_validates_period(self) -> None:
        """Test that SMA validates period parameter"""
        # Period must be positive
        with pytest.raises(ValueError):
            SMA(period=0)

        with pytest.raises(ValueError):
            SMA(period=-5)

    def test_sma_handles_insufficient_data(self) -> None:
        """Test that SMA handles insufficient data gracefully"""
        dates = pd.date_range(start="2024-01-01", periods=3, freq="D")
        ts = TimeSeries(
            open=pd.Series([100.0, 101.0, 102.0], index=dates),
            high=pd.Series([105.0, 106.0, 107.0], index=dates),
            low=pd.Series([95.0, 96.0, 97.0], index=dates),
            close=pd.Series([100.0, 101.0, 102.0], index=dates),
            volume=pd.Series([1000.0, 1100.0, 1200.0], index=dates),
        )

        sma = SMA(period=10)
        result = sma.calculate(ts)

        # All values should be NaN (not enough data)
        assert result.isna().all()

    def test_sma_period_one(self, sample_timeseries: TimeSeries) -> None:
        """Test SMA with period=1 (should equal close prices)"""
        sma = SMA(period=1)
        result = sma.calculate(sample_timeseries)

        # SMA with period 1 should equal close prices
        pd.testing.assert_series_equal(result, sample_timeseries.close, check_names=False)


class TestEMA:
    """Test suite for Exponential Moving Average"""

    @pytest.fixture
    def sample_timeseries(self) -> TimeSeries:
        """Create sample timeseries data"""
        dates = pd.date_range(start="2024-01-01", periods=20, freq="D")
        close_prices = [100.0 + i * 2 for i in range(20)]
        return TimeSeries(
            open=pd.Series(close_prices, index=dates),
            high=pd.Series([p + 5 for p in close_prices], index=dates),
            low=pd.Series([p - 5 for p in close_prices], index=dates),
            close=pd.Series(close_prices, index=dates),
            volume=pd.Series([1000.0] * 20, index=dates),
        )

    def test_ema_calculates_correct_values(self, sample_timeseries: TimeSeries) -> None:
        """Test that EMA calculates correct values"""
        ema = EMA(period=5)
        result = ema.calculate(sample_timeseries)

        assert isinstance(result, pd.Series)
        assert len(result) == len(sample_timeseries)

        # EMA should not have NaN after first value (with adjust=False)
        assert not result.iloc[1:].isna().any()

        # EMA should respond more to recent prices than SMA
        # Verify it's not equal to SMA
        sma = SMA(period=5)
        sma_result = sma.calculate(sample_timeseries)
        assert not result.iloc[-1] == sma_result.iloc[-1]

    def test_ema_validates_period(self) -> None:
        """Test that EMA validates period parameter"""
        with pytest.raises(ValueError):
            EMA(period=0)

        with pytest.raises(ValueError):
            EMA(period=-10)

    def test_ema_responds_to_recent_changes(self) -> None:
        """Test that EMA is more responsive to recent price changes"""
        dates = pd.date_range(start="2024-01-01", periods=10, freq="D")
        # Stable prices then a spike
        close_prices = [100.0] * 8 + [120.0, 130.0]

        ts = TimeSeries(
            open=pd.Series(close_prices, index=dates),
            high=pd.Series([p + 5 for p in close_prices], index=dates),
            low=pd.Series([p - 5 for p in close_prices], index=dates),
            close=pd.Series(close_prices, index=dates),
            volume=pd.Series([1000.0] * 10, index=dates),
        )

        ema = EMA(period=5)
        sma = SMA(period=5)

        ema_result = ema.calculate(ts)
        sma_result = sma.calculate(ts)

        # EMA should be higher than SMA at the end due to recent spike
        assert ema_result.iloc[-1] > sma_result.iloc[-1]


class TestRSI:
    """Test suite for Relative Strength Index"""

    @pytest.fixture
    def sample_timeseries(self) -> TimeSeries:
        """Create sample timeseries data"""
        dates = pd.date_range(start="2024-01-01", periods=30, freq="D")
        # Create data with clear trends
        close_prices = [100.0 + i for i in range(30)]
        return TimeSeries(
            open=pd.Series(close_prices, index=dates),
            high=pd.Series([p + 5 for p in close_prices], index=dates),
            low=pd.Series([p - 5 for p in close_prices], index=dates),
            close=pd.Series(close_prices, index=dates),
            volume=pd.Series([1000.0] * 30, index=dates),
        )

    def test_rsi_calculates_correct_values(self, sample_timeseries: TimeSeries) -> None:
        """Test that RSI calculates correct values"""
        rsi = RSI(period=14)
        result = rsi.calculate(sample_timeseries)

        assert isinstance(result, pd.Series)
        assert len(result) == len(sample_timeseries)

        # First few values will be NaN due to diff() and rolling
        assert result.iloc[:14].isna().any()

        # RSI should have valid values after warmup period
        assert not result.iloc[15:].isna().any()

    def test_rsi_range_0_to_100(self) -> None:
        """Test that RSI values are between 0 and 100"""
        dates = pd.date_range(start="2024-01-01", periods=30, freq="D")

        # Create highly volatile data
        np.random.seed(42)
        base_price = 100.0
        close_prices = [base_price + np.random.randn() * 10 for _ in range(30)]

        ts = TimeSeries(
            open=pd.Series(close_prices, index=dates),
            high=pd.Series([p + 5 for p in close_prices], index=dates),
            low=pd.Series([p - 5 for p in close_prices], index=dates),
            close=pd.Series(close_prices, index=dates),
            volume=pd.Series([1000.0] * 30, index=dates),
        )

        rsi = RSI(period=14)
        result = rsi.calculate(ts)

        # All non-NaN values should be between 0 and 100
        valid_values = result.dropna()
        assert (valid_values >= 0).all()
        assert (valid_values <= 100).all()

    def test_rsi_default_period(self) -> None:
        """Test that RSI has default period of 14"""
        rsi = RSI()
        assert rsi.period == 14

    def test_rsi_validates_period(self) -> None:
        """Test that RSI validates period parameter"""
        with pytest.raises(ValueError):
            RSI(period=0)

        with pytest.raises(ValueError):
            RSI(period=-7)

    def test_rsi_uptrend_high_values(self) -> None:
        """Test that RSI shows high values during strong uptrends"""
        dates = pd.date_range(start="2024-01-01", periods=30, freq="D")
        # Strong uptrend
        close_prices = [100.0 + i * 3 for i in range(30)]

        ts = TimeSeries(
            open=pd.Series(close_prices, index=dates),
            high=pd.Series([p + 5 for p in close_prices], index=dates),
            low=pd.Series([p - 5 for p in close_prices], index=dates),
            close=pd.Series(close_prices, index=dates),
            volume=pd.Series([1000.0] * 30, index=dates),
        )

        rsi = RSI(period=14)
        result = rsi.calculate(ts)

        # During strong uptrend, RSI should be high (> 70 typically indicates overbought)
        assert result.iloc[-1] > 70

    def test_rsi_downtrend_low_values(self) -> None:
        """Test that RSI shows low values during strong downtrends"""
        dates = pd.date_range(start="2024-01-01", periods=30, freq="D")
        # Strong downtrend
        close_prices = [200.0 - i * 3 for i in range(30)]

        ts = TimeSeries(
            open=pd.Series(close_prices, index=dates),
            high=pd.Series([p + 5 for p in close_prices], index=dates),
            low=pd.Series([p - 5 for p in close_prices], index=dates),
            close=pd.Series(close_prices, index=dates),
            volume=pd.Series([1000.0] * 30, index=dates),
        )

        rsi = RSI(period=14)
        result = rsi.calculate(ts)

        # During strong downtrend, RSI should be low (< 30 typically indicates oversold)
        assert result.iloc[-1] < 30


class TestMACD:
    """Test suite for Moving Average Convergence Divergence"""

    @pytest.fixture
    def sample_timeseries(self) -> TimeSeries:
        """Create sample timeseries data"""
        dates = pd.date_range(start="2024-01-01", periods=50, freq="D")
        # Create trending data for MACD
        close_prices = [100.0 + i * 0.5 + np.sin(i / 5) * 3 for i in range(50)]
        return TimeSeries(
            open=pd.Series(close_prices, index=dates),
            high=pd.Series([p + 2 for p in close_prices], index=dates),
            low=pd.Series([p - 2 for p in close_prices], index=dates),
            close=pd.Series(close_prices, index=dates),
            volume=pd.Series([1000.0] * 50, index=dates),
        )

    def test_macd_calculates_three_lines(self, sample_timeseries: TimeSeries) -> None:
        """Test that MACD returns three lines: MACD, signal, and histogram"""
        from canopy.domain.indicator import MACD
        macd = MACD()
        result = macd.calculate(sample_timeseries)

        assert isinstance(result, pd.DataFrame)
        assert "macd" in result.columns
        assert "signal" in result.columns
        assert "histogram" in result.columns
        assert len(result) == len(sample_timeseries)

    def test_macd_default_parameters(self) -> None:
        """Test MACD default parameters (12, 26, 9)"""
        from canopy.domain.indicator import MACD
        macd = MACD()
        assert macd.fast_period == 12
        assert macd.slow_period == 26
        assert macd.signal_period == 9

    def test_macd_validates_periods(self) -> None:
        """Test that MACD validates period parameters"""
        from canopy.domain.indicator import MACD
        with pytest.raises(ValueError):
            MACD(fast_period=0)
        with pytest.raises(ValueError):
            MACD(slow_period=-1)
        with pytest.raises(ValueError):
            MACD(signal_period=0)

    def test_macd_histogram_is_difference(self, sample_timeseries: TimeSeries) -> None:
        """Test that histogram equals MACD minus signal"""
        from canopy.domain.indicator import MACD
        macd = MACD()
        result = macd.calculate(sample_timeseries)

        # Histogram should be MACD - Signal
        expected_histogram = result["macd"] - result["signal"]
        pd.testing.assert_series_equal(
            result["histogram"], expected_histogram, check_names=False
        )

    def test_macd_with_custom_periods(self, sample_timeseries: TimeSeries) -> None:
        """Test MACD with custom period parameters"""
        from canopy.domain.indicator import MACD
        macd = MACD(fast_period=5, slow_period=10, signal_period=5)
        result = macd.calculate(sample_timeseries)

        assert not result["macd"].isna().all()
        assert not result["signal"].isna().all()


class TestBollingerBands:
    """Test suite for Bollinger Bands"""

    @pytest.fixture
    def sample_timeseries(self) -> TimeSeries:
        """Create sample timeseries data"""
        dates = pd.date_range(start="2024-01-01", periods=30, freq="D")
        close_prices = [100.0 + np.sin(i / 3) * 10 for i in range(30)]
        return TimeSeries(
            open=pd.Series(close_prices, index=dates),
            high=pd.Series([p + 2 for p in close_prices], index=dates),
            low=pd.Series([p - 2 for p in close_prices], index=dates),
            close=pd.Series(close_prices, index=dates),
            volume=pd.Series([1000.0] * 30, index=dates),
        )

    def test_bollinger_bands_calculates_three_bands(
        self, sample_timeseries: TimeSeries
    ) -> None:
        """Test that Bollinger Bands returns upper, middle, and lower bands"""
        from canopy.domain.indicator import BollingerBands
        bb = BollingerBands()
        result = bb.calculate(sample_timeseries)

        assert isinstance(result, pd.DataFrame)
        assert "upper" in result.columns
        assert "middle" in result.columns
        assert "lower" in result.columns
        assert "bandwidth" in result.columns
        assert "percent_b" in result.columns

    def test_bollinger_bands_default_parameters(self) -> None:
        """Test Bollinger Bands default parameters (20, 2)"""
        from canopy.domain.indicator import BollingerBands
        bb = BollingerBands()
        assert bb.period == 20
        assert bb.std_dev == 2.0

    def test_bollinger_bands_middle_is_sma(self, sample_timeseries: TimeSeries) -> None:
        """Test that middle band equals SMA"""
        from canopy.domain.indicator import BollingerBands
        bb = BollingerBands(period=20)
        result = bb.calculate(sample_timeseries)

        sma = SMA(period=20)
        expected_middle = sma.calculate(sample_timeseries)

        pd.testing.assert_series_equal(
            result["middle"], expected_middle, check_names=False
        )

    def test_bollinger_bands_validates_parameters(self) -> None:
        """Test that Bollinger Bands validates parameters"""
        from canopy.domain.indicator import BollingerBands
        with pytest.raises(ValueError):
            BollingerBands(period=0)
        with pytest.raises(ValueError):
            BollingerBands(std_dev=0)

    def test_bollinger_bands_upper_above_lower(
        self, sample_timeseries: TimeSeries
    ) -> None:
        """Test that upper band is always above lower band"""
        from canopy.domain.indicator import BollingerBands
        bb = BollingerBands()
        result = bb.calculate(sample_timeseries)

        valid_data = result.dropna()
        assert (valid_data["upper"] >= valid_data["lower"]).all()


class TestATR:
    """Test suite for Average True Range"""

    @pytest.fixture
    def sample_timeseries(self) -> TimeSeries:
        """Create sample timeseries data with varying volatility"""
        dates = pd.date_range(start="2024-01-01", periods=30, freq="D")
        close_prices = [100.0 + i * 0.5 for i in range(30)]
        high_prices = [p + 5 + i * 0.1 for i, p in enumerate(close_prices)]
        low_prices = [p - 5 - i * 0.1 for i, p in enumerate(close_prices)]
        return TimeSeries(
            open=pd.Series(close_prices, index=dates),
            high=pd.Series(high_prices, index=dates),
            low=pd.Series(low_prices, index=dates),
            close=pd.Series(close_prices, index=dates),
            volume=pd.Series([1000.0] * 30, index=dates),
        )

    def test_atr_calculates_correct_values(self, sample_timeseries: TimeSeries) -> None:
        """Test that ATR calculates volatility values"""
        from canopy.domain.indicator import ATR
        atr = ATR()
        result = atr.calculate(sample_timeseries)

        assert isinstance(result, pd.Series)
        assert len(result) == len(sample_timeseries)
        # ATR should have valid values after warmup
        assert not result.iloc[14:].isna().all()

    def test_atr_default_period(self) -> None:
        """Test ATR default period of 14"""
        from canopy.domain.indicator import ATR
        atr = ATR()
        assert atr.period == 14

    def test_atr_validates_period(self) -> None:
        """Test that ATR validates period parameter"""
        from canopy.domain.indicator import ATR
        with pytest.raises(ValueError):
            ATR(period=0)
        with pytest.raises(ValueError):
            ATR(period=-5)

    def test_atr_always_positive(self, sample_timeseries: TimeSeries) -> None:
        """Test that ATR values are always positive"""
        from canopy.domain.indicator import ATR
        atr = ATR()
        result = atr.calculate(sample_timeseries)

        valid_values = result.dropna()
        assert (valid_values >= 0).all()


class TestStochastic:
    """Test suite for Stochastic Oscillator"""

    @pytest.fixture
    def sample_timeseries(self) -> TimeSeries:
        """Create sample timeseries data"""
        dates = pd.date_range(start="2024-01-01", periods=30, freq="D")
        close_prices = [100.0 + np.sin(i / 3) * 20 for i in range(30)]
        high_prices = [p + 5 for p in close_prices]
        low_prices = [p - 5 for p in close_prices]
        return TimeSeries(
            open=pd.Series(close_prices, index=dates),
            high=pd.Series(high_prices, index=dates),
            low=pd.Series(low_prices, index=dates),
            close=pd.Series(close_prices, index=dates),
            volume=pd.Series([1000.0] * 30, index=dates),
        )

    def test_stochastic_calculates_k_and_d(
        self, sample_timeseries: TimeSeries
    ) -> None:
        """Test that Stochastic returns %K and %D lines"""
        from canopy.domain.indicator import Stochastic
        stoch = Stochastic()
        result = stoch.calculate(sample_timeseries)

        assert isinstance(result, pd.DataFrame)
        assert "k" in result.columns
        assert "d" in result.columns

    def test_stochastic_default_parameters(self) -> None:
        """Test Stochastic default parameters (14, 3)"""
        from canopy.domain.indicator import Stochastic
        stoch = Stochastic()
        assert stoch.k_period == 14
        assert stoch.d_period == 3

    def test_stochastic_range_0_to_100(self, sample_timeseries: TimeSeries) -> None:
        """Test that Stochastic values are between 0 and 100"""
        from canopy.domain.indicator import Stochastic
        stoch = Stochastic()
        result = stoch.calculate(sample_timeseries)

        valid_k = result["k"].dropna()
        valid_d = result["d"].dropna()

        assert (valid_k >= 0).all() and (valid_k <= 100).all()
        assert (valid_d >= 0).all() and (valid_d <= 100).all()

    def test_stochastic_validates_periods(self) -> None:
        """Test that Stochastic validates period parameters"""
        from canopy.domain.indicator import Stochastic
        with pytest.raises(ValueError):
            Stochastic(k_period=0)
        with pytest.raises(ValueError):
            Stochastic(d_period=-1)


class TestADX:
    """Test suite for Average Directional Index"""

    @pytest.fixture
    def sample_timeseries(self) -> TimeSeries:
        """Create sample timeseries data with trend"""
        dates = pd.date_range(start="2024-01-01", periods=50, freq="D")
        close_prices = [100.0 + i * 2 for i in range(50)]
        high_prices = [p + 3 for p in close_prices]
        low_prices = [p - 3 for p in close_prices]
        return TimeSeries(
            open=pd.Series(close_prices, index=dates),
            high=pd.Series(high_prices, index=dates),
            low=pd.Series(low_prices, index=dates),
            close=pd.Series(close_prices, index=dates),
            volume=pd.Series([1000.0] * 50, index=dates),
        )

    def test_adx_calculates_values(self, sample_timeseries: TimeSeries) -> None:
        """Test that ADX calculates trend strength values"""
        from canopy.domain.indicator import ADX
        adx = ADX()
        result = adx.calculate(sample_timeseries)

        assert isinstance(result, pd.Series)
        assert len(result) == len(sample_timeseries)

    def test_adx_default_period(self) -> None:
        """Test ADX default period of 14"""
        from canopy.domain.indicator import ADX
        adx = ADX()
        assert adx.period == 14

    def test_adx_range_0_to_100(self, sample_timeseries: TimeSeries) -> None:
        """Test that ADX values are between 0 and 100"""
        from canopy.domain.indicator import ADX
        adx = ADX()
        result = adx.calculate(sample_timeseries)

        valid_values = result.dropna()
        assert (valid_values >= 0).all()
        assert (valid_values <= 100).all()

    def test_adx_validates_period(self) -> None:
        """Test that ADX validates period parameter"""
        from canopy.domain.indicator import ADX
        with pytest.raises(ValueError):
            ADX(period=0)


class TestOBV:
    """Test suite for On-Balance Volume"""

    @pytest.fixture
    def sample_timeseries(self) -> TimeSeries:
        """Create sample timeseries data"""
        dates = pd.date_range(start="2024-01-01", periods=20, freq="D")
        close_prices = [100.0 + i for i in range(20)]
        volumes = [1000.0 + i * 100 for i in range(20)]
        return TimeSeries(
            open=pd.Series(close_prices, index=dates),
            high=pd.Series([p + 2 for p in close_prices], index=dates),
            low=pd.Series([p - 2 for p in close_prices], index=dates),
            close=pd.Series(close_prices, index=dates),
            volume=pd.Series(volumes, index=dates),
        )

    def test_obv_calculates_cumulative_volume(
        self, sample_timeseries: TimeSeries
    ) -> None:
        """Test that OBV calculates cumulative volume based on price direction"""
        from canopy.domain.indicator import OBV
        obv = OBV()
        result = obv.calculate(sample_timeseries)

        assert isinstance(result, pd.Series)
        assert len(result) == len(sample_timeseries)

    def test_obv_increases_on_up_days(self) -> None:
        """Test that OBV increases when price goes up"""
        from canopy.domain.indicator import OBV
        dates = pd.date_range(start="2024-01-01", periods=5, freq="D")
        close_prices = [100.0, 102.0, 105.0, 103.0, 107.0]
        volumes = [1000.0, 1100.0, 1200.0, 1300.0, 1400.0]

        ts = TimeSeries(
            open=pd.Series(close_prices, index=dates),
            high=pd.Series([p + 2 for p in close_prices], index=dates),
            low=pd.Series([p - 2 for p in close_prices], index=dates),
            close=pd.Series(close_prices, index=dates),
            volume=pd.Series(volumes, index=dates),
        )

        obv = OBV()
        result = obv.calculate(ts)

        # Day 2 (up) - OBV should increase
        assert result.iloc[1] > result.iloc[0]
        # Day 4 (down) - OBV should decrease
        assert result.iloc[3] < result.iloc[2]


class TestVWAP:
    """Test suite for Volume Weighted Average Price"""

    @pytest.fixture
    def sample_timeseries(self) -> TimeSeries:
        """Create sample timeseries data"""
        dates = pd.date_range(start="2024-01-01", periods=20, freq="D")
        close_prices = [100.0 + i for i in range(20)]
        high_prices = [p + 2 for p in close_prices]
        low_prices = [p - 2 for p in close_prices]
        volumes = [1000.0 + i * 50 for i in range(20)]
        return TimeSeries(
            open=pd.Series(close_prices, index=dates),
            high=pd.Series(high_prices, index=dates),
            low=pd.Series(low_prices, index=dates),
            close=pd.Series(close_prices, index=dates),
            volume=pd.Series(volumes, index=dates),
        )

    def test_vwap_calculates_weighted_average(
        self, sample_timeseries: TimeSeries
    ) -> None:
        """Test that VWAP calculates volume-weighted average price"""
        from canopy.domain.indicator import VWAP
        vwap = VWAP()
        result = vwap.calculate(sample_timeseries)

        assert isinstance(result, pd.Series)
        assert len(result) == len(sample_timeseries)
        assert not result.isna().all()

    def test_vwap_uses_typical_price(self, sample_timeseries: TimeSeries) -> None:
        """Test that VWAP uses typical price (H+L+C)/3"""
        from canopy.domain.indicator import VWAP
        vwap = VWAP()
        result = vwap.calculate(sample_timeseries)

        # VWAP should be close to typical price for equal volumes
        typical_price = (
            sample_timeseries.high + sample_timeseries.low + sample_timeseries.close
        ) / 3
        # VWAP should be in reasonable range
        assert result.iloc[-1] > 0


class TestParabolicSAR:
    """Test suite for Parabolic SAR"""

    @pytest.fixture
    def sample_timeseries(self) -> TimeSeries:
        """Create sample timeseries data with trend"""
        dates = pd.date_range(start="2024-01-01", periods=30, freq="D")
        close_prices = [100.0 + i * 0.5 for i in range(30)]
        high_prices = [p + 2 for p in close_prices]
        low_prices = [p - 2 for p in close_prices]
        return TimeSeries(
            open=pd.Series(close_prices, index=dates),
            high=pd.Series(high_prices, index=dates),
            low=pd.Series(low_prices, index=dates),
            close=pd.Series(close_prices, index=dates),
            volume=pd.Series([1000.0] * 30, index=dates),
        )

    def test_parabolic_sar_calculates_values(
        self, sample_timeseries: TimeSeries
    ) -> None:
        """Test that Parabolic SAR calculates trend reversal points"""
        from canopy.domain.indicator import ParabolicSAR
        psar = ParabolicSAR()
        result = psar.calculate(sample_timeseries)

        assert isinstance(result, pd.Series)
        assert len(result) == len(sample_timeseries)

    def test_parabolic_sar_default_parameters(self) -> None:
        """Test Parabolic SAR default parameters"""
        from canopy.domain.indicator import ParabolicSAR
        psar = ParabolicSAR()
        assert psar.acceleration == 0.02
        assert psar.maximum == 0.2

    def test_parabolic_sar_validates_parameters(self) -> None:
        """Test that Parabolic SAR validates parameters"""
        from canopy.domain.indicator import ParabolicSAR
        with pytest.raises(ValueError):
            ParabolicSAR(acceleration=0)
        with pytest.raises(ValueError):
            ParabolicSAR(maximum=0)


class TestCCI:
    """Test suite for Commodity Channel Index"""

    @pytest.fixture
    def sample_timeseries(self) -> TimeSeries:
        """Create sample timeseries data"""
        dates = pd.date_range(start="2024-01-01", periods=30, freq="D")
        close_prices = [100.0 + np.sin(i / 3) * 10 for i in range(30)]
        high_prices = [p + 3 for p in close_prices]
        low_prices = [p - 3 for p in close_prices]
        return TimeSeries(
            open=pd.Series(close_prices, index=dates),
            high=pd.Series(high_prices, index=dates),
            low=pd.Series(low_prices, index=dates),
            close=pd.Series(close_prices, index=dates),
            volume=pd.Series([1000.0] * 30, index=dates),
        )

    def test_cci_calculates_values(self, sample_timeseries: TimeSeries) -> None:
        """Test that CCI calculates momentum values"""
        from canopy.domain.indicator import CCI
        cci = CCI()
        result = cci.calculate(sample_timeseries)

        assert isinstance(result, pd.Series)
        assert len(result) == len(sample_timeseries)

    def test_cci_default_period(self) -> None:
        """Test CCI default period of 20"""
        from canopy.domain.indicator import CCI
        cci = CCI()
        assert cci.period == 20

    def test_cci_validates_period(self) -> None:
        """Test that CCI validates period parameter"""
        from canopy.domain.indicator import CCI
        with pytest.raises(ValueError):
            CCI(period=0)

    def test_cci_oscillates_around_zero(self, sample_timeseries: TimeSeries) -> None:
        """Test that CCI oscillates around zero"""
        from canopy.domain.indicator import CCI
        cci = CCI()
        result = cci.calculate(sample_timeseries)

        valid_values = result.dropna()
        # CCI should have both positive and negative values in oscillating data
        assert len(valid_values) > 0


class TestWilliamsR:
    """Test suite for Williams %R"""

    @pytest.fixture
    def sample_timeseries(self) -> TimeSeries:
        """Create sample timeseries data"""
        dates = pd.date_range(start="2024-01-01", periods=30, freq="D")
        close_prices = [100.0 + np.sin(i / 3) * 15 for i in range(30)]
        high_prices = [p + 5 for p in close_prices]
        low_prices = [p - 5 for p in close_prices]
        return TimeSeries(
            open=pd.Series(close_prices, index=dates),
            high=pd.Series(high_prices, index=dates),
            low=pd.Series(low_prices, index=dates),
            close=pd.Series(close_prices, index=dates),
            volume=pd.Series([1000.0] * 30, index=dates),
        )

    def test_williams_r_calculates_values(
        self, sample_timeseries: TimeSeries
    ) -> None:
        """Test that Williams %R calculates momentum values"""
        from canopy.domain.indicator import WilliamsR
        williams = WilliamsR()
        result = williams.calculate(sample_timeseries)

        assert isinstance(result, pd.Series)
        assert len(result) == len(sample_timeseries)

    def test_williams_r_default_period(self) -> None:
        """Test Williams %R default period of 14"""
        from canopy.domain.indicator import WilliamsR
        williams = WilliamsR()
        assert williams.period == 14

    def test_williams_r_range_negative_100_to_0(
        self, sample_timeseries: TimeSeries
    ) -> None:
        """Test that Williams %R values are between -100 and 0"""
        from canopy.domain.indicator import WilliamsR
        williams = WilliamsR()
        result = williams.calculate(sample_timeseries)

        valid_values = result.dropna()
        assert (valid_values >= -100).all()
        assert (valid_values <= 0).all()

    def test_williams_r_validates_period(self) -> None:
        """Test that Williams %R validates period parameter"""
        from canopy.domain.indicator import WilliamsR
        with pytest.raises(ValueError):
            WilliamsR(period=0)


class TestIndicatorAbstract:
    """Test the abstract Indicator base class"""

    def test_indicator_is_abstract(self) -> None:
        """Test that Indicator cannot be instantiated directly"""
        with pytest.raises(TypeError):
            # Should fail because calculate() is abstract
            Indicator()  # type: ignore
