# Canopy Language Reference

## Overview

Canopy is a domain-specific language (DSL) designed for trading strategy development. It provides a simple, expressive syntax for defining technical indicators, trading signals, and visualizations.

## Basic Syntax

### Strategy Declaration

Every Canopy strategy must start with a strategy declaration:

```canopy
strategy "Strategy Name"
```

### Comments

```canopy
# This is a comment
# Comments start with # and go to the end of the line
```

### Variables

Variables are defined using assignment:

```canopy
my_variable = sma(close, 20)
fast_ma = ema(close, 12)
```

## Built-in Data Series

These series are automatically available in every strategy:

| Series | Description |
|--------|-------------|
| `open` | Opening price |
| `high` | High price |
| `low` | Low price |
| `close` | Closing price |
| `volume` | Trading volume |

## Technical Indicators

### Moving Averages

#### Simple Moving Average (SMA)

Calculates the arithmetic mean over a period.

```canopy
sma(data, period)
```

**Parameters**:
- `data`: Input data series (e.g., close, open)
- `period`: Number of periods

**Examples**:
```canopy
ma20 = sma(close, 20)
ma50 = sma(close, 50)
ma200 = sma(close, 200)
```

#### Exponential Moving Average (EMA)

Gives more weight to recent prices.

```canopy
ema(data, period)
```

**Parameters**:
- `data`: Input data series
- `period`: Number of periods

**Examples**:
```canopy
ema12 = ema(close, 12)
ema26 = ema(close, 26)
```

#### Weighted Moving Average (WMA)

Linear weighted moving average.

```canopy
wma(data, period)
```

### Momentum Indicators

#### Relative Strength Index (RSI)

Measures momentum on a scale of 0-100.

```canopy
rsi(data, period=14)
```

**Parameters**:
- `data`: Input data series
- `period`: Lookback period (default: 14)

**Examples**:
```canopy
rsi14 = rsi(close, 14)
buy when rsi14 < 30   # Oversold
sell when rsi14 > 70  # Overbought
```

#### Moving Average Convergence Divergence (MACD)

Trend-following momentum indicator.

```canopy
macd(data, fast=12, slow=26, signal=9)
```

**Returns**: Three series (macd_line, signal_line, histogram)

**Examples**:
```canopy
macd_line, signal_line, histogram = macd(close)
buy when crossover(macd_line, signal_line)
sell when crossunder(macd_line, signal_line)
```

#### Stochastic Oscillator

Compares closing price to price range.

```canopy
stochastic(k_period=14, d_period=3)
```

**Examples**:
```canopy
k, d = stochastic(14, 3)
buy when k < 20 and crossover(k, d)
sell when k > 80
```

#### Rate of Change (ROC)

Measures percentage change.

```canopy
roc(data, period)
```

### Volatility Indicators

#### Bollinger Bands

Price envelope defined by standard deviations.

```canopy
bollinger_bands(data, period=20, std_dev=2.0)
```

**Returns**: Three series (upper, middle, lower)

**Examples**:
```canopy
upper, middle, lower = bollinger_bands(close, 20, 2.0)
buy when close < lower
sell when close > upper
```

#### Average True Range (ATR)

Measures market volatility.

```canopy
atr(period=14)
```

**Examples**:
```canopy
atr14 = atr(14)
stop_loss = close - (2 * atr14)
```

#### Standard Deviation

```canopy
std(data, period)
```

### Trend Indicators

#### Average Directional Index (ADX)

Measures trend strength (not direction).

```canopy
adx(period=14)
```

**Examples**:
```canopy
adx14 = adx(14)
# ADX > 25 indicates strong trend
# ADX < 20 indicates weak trend
```

#### Parabolic SAR

Stop and reverse indicator.

```canopy
sar(acceleration=0.02, maximum=0.2)
```

#### Ichimoku Cloud

```canopy
ichimoku()
```

### Volume Indicators

#### On-Balance Volume (OBV)

```canopy
obv()
```

#### Volume Weighted Average Price (VWAP)

```canopy
vwap()
```

## Signal Functions

### Crossover Functions

#### Crossover

Detects when series1 crosses above series2.

```canopy
crossover(series1, series2)
```

**Examples**:
```canopy
buy when crossover(fast_ma, slow_ma)
```

#### Crossunder

Detects when series1 crosses below series2.

```canopy
crossunder(series1, series2)
```

**Examples**:
```canopy
sell when crossunder(fast_ma, slow_ma)
```

### Comparison Operators

```canopy
>   # Greater than
<   # Less than
>=  # Greater than or equal
<=  # Less than or equal
==  # Equal to
!=  # Not equal to
```

### Logical Operators

```canopy
and  # Logical AND
or   # Logical OR
not  # Logical NOT
```

**Examples**:
```canopy
buy when rsi < 30 and close > sma(close, 200)
sell when rsi > 70 or close < stop_loss
```

## Trading Signals

### Buy Signals

```canopy
buy when <condition>
```

**Examples**:
```canopy
# Simple condition
buy when close > sma(close, 50)

# Multiple conditions
buy when crossover(fast_ma, slow_ma) and volume > sma(volume, 20)

# Complex conditions
buy when (rsi < 30 and close > lower_band) or momentum > 0
```

### Sell Signals

```canopy
sell when <condition>
```

**Examples**:
```canopy
# Simple condition
sell when close < sma(close, 50)

# Multiple conditions
sell when crossunder(fast_ma, slow_ma) or rsi > 70

# Trailing stop
sell when close < (highest_close * 0.95)
```

### Entry and Exit Management

```canopy
# Percentage-based stops
buy when condition
sell when close < entry_price * 0.95  # 5% stop loss

# ATR-based stops
atr_value = atr(14)
buy when condition
sell when close < entry_price - (2 * atr_value)

# Time-based exits
sell after 10 bars  # Exit after 10 periods
```

## Plotting

### Plot Function

Visualize indicators and data series.

```canopy
plot(series, name, color=<color>, style=<style>)
```

**Parameters**:
- `series`: Data to plot
- `name`: Display name (string)
- `color`: Color (optional): blue, red, green, yellow, purple, orange, etc.
- `style`: Style (optional): line, dashed, dotted, area

**Examples**:
```canopy
# Plot moving averages
plot(fast_ma, "Fast MA (50)", color=blue)
plot(slow_ma, "Slow MA (200)", color=red)

# Plot RSI with levels
plot(rsi14, "RSI", color=purple)
plot(30, "Oversold", color=green, style=dashed)
plot(70, "Overbought", color=red, style=dashed)

# Plot Bollinger Bands
upper, middle, lower = bollinger_bands(close, 20, 2.0)
plot(upper, "Upper Band", color=red, style=dashed)
plot(middle, "Middle Band", color=blue)
plot(lower, "Lower Band", color=green, style=dashed)
```

## Complete Strategy Examples

### Example 1: Moving Average Crossover

```canopy
strategy "MA Crossover"

# Define moving averages
fast_ma = sma(close, 50)
slow_ma = sma(close, 200)

# Entry signal: Buy when fast MA crosses above slow MA
buy when crossover(fast_ma, slow_ma)

# Exit signal: Sell when fast MA crosses below slow MA
sell when crossunder(fast_ma, slow_ma)

# Plot indicators
plot(fast_ma, "Fast MA (50)", color=blue)
plot(slow_ma, "Slow MA (200)", color=red)
```

### Example 2: RSI Mean Reversion

```canopy
strategy "RSI Mean Reversion"

# Calculate RSI
rsi14 = rsi(close, 14)

# Entry when oversold
buy when rsi14 < 30 and close > sma(close, 200)

# Exit when overbought
sell when rsi14 > 70

# Plot RSI and levels
plot(rsi14, "RSI", color=purple)
plot(30, "Oversold", color=green, style=dashed)
plot(70, "Overbought", color=red, style=dashed)
```

### Example 3: Bollinger Band Squeeze

```canopy
strategy "Bollinger Squeeze"

# Calculate Bollinger Bands
upper, middle, lower = bollinger_bands(close, 20, 2.0)

# Calculate band width
bandwidth = (upper - lower) / middle

# Entry when price breaks out of squeeze
buy when close > upper and bandwidth < 0.05

# Exit when price returns to middle
sell when close < middle

# Plot bands
plot(upper, "Upper Band", color=red, style=dashed)
plot(middle, "Middle Band", color=blue)
plot(lower, "Lower Band", color=green, style=dashed)
```

### Example 4: MACD Divergence

```canopy
strategy "MACD Divergence"

# Calculate MACD
macd_line, signal_line, histogram = macd(close, 12, 26, 9)

# Entry on bullish crossover
buy when crossover(macd_line, signal_line) and histogram > 0

# Exit on bearish crossover
sell when crossunder(macd_line, signal_line)

# Plot MACD
plot(macd_line, "MACD", color=blue)
plot(signal_line, "Signal", color=red)
plot(histogram, "Histogram", color=green, style=area)
```

### Example 5: Multi-Timeframe Strategy

```canopy
strategy "Multi-Timeframe Trend"

# Daily trend filter
daily_ema = ema(close, 50, timeframe="1D")

# Intraday signals
hourly_rsi = rsi(close, 14, timeframe="1H")

# Only buy when daily trend is up
buy when close > daily_ema and hourly_rsi < 30

# Exit on hourly overbought
sell when hourly_rsi > 70

# Plot
plot(daily_ema, "Daily EMA", color=blue)
plot(hourly_rsi, "Hourly RSI", color=purple)
```

## Advanced Features

### Position Sizing

```canopy
# Fixed size
position_size = 100

# Percentage of capital
position_size = capital * 0.1 / close

# ATR-based sizing
risk_per_trade = capital * 0.02
atr_value = atr(14)
position_size = risk_per_trade / (2 * atr_value)
```

### Risk Management

```canopy
# Stop loss
stop_loss = entry_price * 0.95

# Trailing stop
trailing_stop = highest(close, 20) * 0.95

# Take profit
take_profit = entry_price * 1.10

# Risk-reward ratio
stop_distance = entry_price - stop_loss
target_price = entry_price + (stop_distance * 2)
```

### Multiple Timeframes

```canopy
# Get data from different timeframes
daily_close = close(timeframe="1D")
weekly_close = close(timeframe="1W")
hourly_rsi = rsi(close, 14, timeframe="1H")
```

## Best Practices

### 1. Use Descriptive Names

```canopy
# Good
fast_moving_average = sma(close, 50)
slow_moving_average = sma(close, 200)

# Bad
ma1 = sma(close, 50)
ma2 = sma(close, 200)
```

### 2. Add Comments

```canopy
# Calculate trend-following indicators
fast_ma = sma(close, 50)   # Short-term trend
slow_ma = sma(close, 200)  # Long-term trend

# Entry signal: Golden cross
buy when crossover(fast_ma, slow_ma)
```

### 3. Use Trend Filters

```canopy
# Only trade in direction of major trend
long_term_trend = sma(close, 200)

# Only buy above 200-day MA
buy when crossover(fast_ma, slow_ma) and close > long_term_trend
```

### 4. Implement Risk Management

```canopy
# Always use stop losses
atr_value = atr(14)
stop_loss = entry_price - (2 * atr_value)
sell when close < stop_loss
```

### 5. Test Multiple Conditions

```canopy
# Combine multiple indicators for confirmation
rsi14 = rsi(close, 14)
macd_line, signal_line, _ = macd(close)

# Buy only when multiple conditions align
buy when rsi14 < 40 and crossover(macd_line, signal_line) and volume > sma(volume, 20)
```

## Limitations and Future Features

### Current Limitations
- Single asset per strategy (portfolio support coming)
- Market orders only (limit orders coming)
- No options/futures support yet
- No machine learning integration yet

### Coming Soon
- Portfolio strategies
- Custom indicator creation
- Machine learning integration
- Walk-forward optimization
- Real-time trading integration

## Error Messages

Common errors and how to fix them:

### Syntax Error
```
Error: Unexpected token 'when' on line 5
Fix: Check for typos in keywords
```

### Undefined Variable
```
Error: Variable 'fast_ma' is not defined
Fix: Define variable before using it
```

### Invalid Function
```
Error: Unknown function 'sm' on line 3
Fix: Use 'sma' instead of 'sm'
```

### Type Error
```
Error: Cannot compare series to string
Fix: Ensure you're comparing compatible types
```

## Additional Resources

- **Examples**: See `/examples/strategies/` for more examples
- **API Reference**: See `API_REFERENCE.md`
- **Architecture**: See `ARCHITECTURE.md`
- **Development Guide**: See `DEVELOPMENT.md`
