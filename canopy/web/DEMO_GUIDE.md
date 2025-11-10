# Canopy Web IDE - Demo Guide

## Quick Start Demo (5 minutes)

This guide walks you through a complete demo of the Canopy Web IDE.

### Step 1: Start the Application

```bash
cd /home/user/canopy-lang/canopy/web
npm run dev
```

Open your browser to http://localhost:5173

### Step 2: Explore the Home Page

You'll see:
- Welcome hero section with Canopy branding
- Feature showcase (Monaco Editor, Indicators, Analytics, Charts)
- Quick start guide
- Links to Editor and Documentation

**Action**: Click "Start Coding" button to go to the Editor

### Step 3: Explore the Editor

The Editor page has three main areas:

**Left Panel (optional)**:
- Click "Examples" to see example strategies
- Click "Indicators" to browse indicator library

**Center**: Monaco Editor with a default strategy loaded

**Right**: Backtest configuration panel

### Step 4: Load an Example Strategy

1. Click the "Examples" button in the toolbar
2. Browse the example strategies
3. Click "Moving Average Crossover" (Beginner level)
4. Click "Load Strategy" button
5. The code appears in the editor:

```canopy
strategy "Moving Average Crossover"

// Define moving averages
fast_ma = sma(close, 10)
slow_ma = sma(close, 30)

// Entry condition: Fast MA crosses above Slow MA
buy when crossover(fast_ma, slow_ma)

// Exit condition: Fast MA crosses below Slow MA
sell when crossunder(fast_ma, slow_ma)

// Plot indicators on the chart
plot fast_ma
plot slow_ma
```

### Step 5: Explore Editor Features

**Try these features**:

1. **Syntax Highlighting**: Notice keywords in different colors
2. **Autocomplete**: Type `ema` and press Ctrl+Space to see suggestions
3. **Save**: Press Ctrl+S to save (notice "Unsaved changes" indicator)
4. **Code Folding**: Click the arrow next to line numbers to fold code
5. **Minimap**: See the code overview on the right edge

### Step 6: Browse the Indicator Library

1. Click "Indicators" button
2. Search for "rsi"
3. Click on "Relative Strength Index"
4. View the documentation:
   - Description
   - Syntax
   - Parameters table
   - Example code
5. Click "Insert Code" to add RSI to your strategy

### Step 7: Configure a Backtest

In the right panel:

1. **Symbol**: Enter "AAPL" (or try TSLA, GOOGL, etc.)
2. **Start Date**: Select 2023-01-01
3. **End Date**: Select 2024-01-01
4. **Initial Capital**: Set to $100,000
5. **Advanced Settings**: Expand to see commission and slippage options

### Step 8: Run a Backtest

1. Click the "Run Backtest" button
2. Watch the loading spinner (simulates 2 seconds)
3. Results appear automatically

### Step 9: Analyze Results

The Results panel has three tabs:

**Overview Tab**:
- Four metric cards: Returns, Risk, Trading, Analysis
- Color-coded metrics (green = good, red = bad)
- Key metrics:
  - Total Return: $X,XXX (+X.XX%)
  - Sharpe Ratio: X.XX
  - Max Drawdown: X.XX%
  - Win Rate: XX%
  - Profit Factor: X.XX

**Charts Tab**:
- Equity Curve: Shows account growth over time
- Drawdown Chart: Visualizes peak-to-trough declines
- Interactive tooltips (hover over charts)

**Trades Tab**:
- Complete trade list
- Columns: Date, Type, Price, Quantity, Commission, P&L
- Color-coded P&L (green profits, red losses)
- Scrollable table for large trade lists

### Step 10: Explore the Documentation

1. Click the "Docs" link in navigation
2. Browse through:
   - Getting Started
   - Language Syntax
   - Built-in Variables
   - Indicators
   - Functions
   - Example Strategies
   - Best Practices

### Step 11: Try Writing Your Own Strategy

Go back to the Editor and try this simple RSI strategy:

```canopy
strategy "RSI Mean Reversion"

// Calculate RSI
rsi_value = rsi(close, 14)

// Buy when oversold
buy when rsi_value < 30

// Sell when overbought
sell when rsi_value > 70

// Plot RSI
plot rsi_value
```

**Try**:
1. Type it manually to see autocomplete in action
2. Save with Ctrl+S
3. Run a backtest
4. Compare results with the MA Crossover strategy

### Step 12: Experiment with View Modes

In the Editor toolbar, try different view modes:

- **Editor**: Full-screen editor only
- **Split**: Editor and results side-by-side (default)
- **Results**: Full-screen results only

### Step 13: Toggle Dark/Light Mode

Click the sun/moon icon in the navigation to toggle themes.

## Feature Highlights to Show

### Monaco Editor Features

1. **Autocomplete**:
   - Type `s` and see: sma, sell, strategy
   - Select one and it inserts with parameter placeholders

2. **Find/Replace**:
   - Press Ctrl+F to open find
   - Press Ctrl+H to open replace

3. **Multi-cursor**:
   - Alt+Click to add cursors
   - Edit multiple lines simultaneously

### State Persistence

1. Write a strategy
2. Run a backtest
3. Close the browser tab
4. Reopen http://localhost:5173
5. Notice your backtest history is preserved!

### Example Strategies

**Beginner**:
- MA Crossover
- RSI Mean Reversion

**Intermediate**:
- Bollinger Band Breakout
- MACD Momentum

Each shows increasing complexity and different techniques.

## Common Demo Scenarios

### Scenario 1: "I want to test a simple trend-following strategy"

1. Load "MA Crossover" example
2. Modify periods: change 10/30 to 20/50
3. Run backtest on AAPL
4. Compare metrics

### Scenario 2: "I want to understand indicator parameters"

1. Open Indicator Library
2. Click on "Bollinger Bands"
3. Read parameter descriptions
4. See example code
5. Insert into editor

### Scenario 3: "I want to see performance metrics"

1. Run any backtest
2. Go to Overview tab
3. Explain each metric:
   - Sharpe Ratio: Risk-adjusted returns
   - Max Drawdown: Worst decline
   - Win Rate: % of profitable trades
   - Profit Factor: Gross profit / gross loss

### Scenario 4: "I want to visualize strategy performance"

1. Run a backtest
2. Go to Charts tab
3. Show equity curve: "This is your account growth"
4. Show drawdown: "This shows your worst periods"
5. Hover for specific dates and values

## Tips for a Great Demo

1. **Start with Home Page**: Show the polished landing
2. **Load an Example**: Don't type from scratch initially
3. **Explain as You Go**: Narrate what each feature does
4. **Show Results First**: Run a backtest early to show the payoff
5. **Highlight Monaco**: It's the most impressive feature
6. **Use the Docs**: Show how comprehensive the documentation is
7. **End with Custom Strategy**: Show how easy it is to create your own

## Common Questions During Demo

**Q: Is this real data?**
A: Currently using mock data. Agent 5 will build the real backend with historical data.

**Q: Can I save my strategies?**
A: Yes, they're saved to browser localStorage. Real database coming with backend.

**Q: What indicators are available?**
A: SMA, EMA, RSI, MACD, Bollinger Bands, ATR, and more. See Indicator Library.

**Q: Can I backtest multiple symbols?**
A: Currently one at a time. Portfolio backtesting is a future enhancement.

**Q: How accurate are the results?**
A: Mock data shows realistic patterns. Real accuracy depends on the backend data quality.

**Q: Can I export results?**
A: Not yet, but planned for future (PDF/CSV export).

## Performance Notes for Demo

- **Initial Load**: ~2 seconds (Monaco is large)
- **Backtest Run**: ~2 seconds (simulated, real will vary)
- **Chart Rendering**: Instant
- **Autocomplete**: Instant
- **Syntax Highlighting**: Instant

## Browser Recommendations for Demo

- **Best**: Chrome or Edge (best Monaco performance)
- **Good**: Firefox
- **Works**: Safari

## Conclusion

This demo showcases:
- Professional IDE with Monaco Editor
- Comprehensive backtesting interface
- Rich performance analytics
- Beautiful dark theme
- Intuitive user experience

The Canopy Web IDE makes algorithmic trading accessible to everyone!

---

**For the full technical report**, see AGENT4_SUMMARY.md

**For setup instructions**, see README.md
