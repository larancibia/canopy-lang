# Canopy Web IDE

A modern, web-based IDE for developing and backtesting algorithmic trading strategies using the Canopy domain-specific language.

## Features

### Monaco Editor Integration
- Full VS Code editor experience in the browser
- Syntax highlighting for Canopy language
- Intelligent autocomplete for indicators and functions
- Real-time error detection
- Code folding, minimap, and bracket matching

### Strategy Development
- Write strategies using intuitive DSL
- Built-in indicators: SMA, EMA, RSI, MACD, Bollinger Bands, ATR, and more
- Helper functions: crossover, crossunder, highest, lowest
- Example strategy library

### Backtesting Engine
- Configure backtest parameters (symbol, date range, capital)
- Advanced settings (commission, slippage)
- Real-time backtest execution (mock data for now)
- Comprehensive performance metrics

### Performance Analytics
- **Returns**: Total return, return %, Sharpe ratio, Sortino ratio
- **Risk**: Max drawdown, Calmar ratio
- **Trading**: Win rate, profit factor, trade statistics
- **Analysis**: Average win/loss, expectancy, trade duration

### Visualization
- Interactive equity curve charts
- Drawdown visualization
- Trade-by-trade performance table
- Responsive charts using Recharts

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Fast build tool and dev server
- **Monaco Editor** - VS Code editor component
- **TailwindCSS** - Utility-first CSS framework
- **Recharts** - Charting library
- **React Router** - Client-side routing
- **Zustand** - State management

## Setup Instructions

### Prerequisites

- Node.js 18+ and npm

### Installation

1. Navigate to the web directory:
```bash
cd /home/user/canopy-lang/canopy/web
```

2. Install dependencies (if not already done):
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

4. Open your browser to the URL shown (typically http://localhost:5173)

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Usage Guide

### Writing a Strategy

Navigate to the Editor page and write your strategy using Canopy's DSL:

```canopy
strategy "My Strategy"

// Define indicators
fast_ma = sma(close, 10)
slow_ma = sma(close, 30)

// Entry condition
buy when crossover(fast_ma, slow_ma)

// Exit condition
sell when crossunder(fast_ma, slow_ma)

// Plot indicators
plot fast_ma
plot slow_ma
```

**Keyboard Shortcuts:**
- `Ctrl+S` (or `Cmd+S` on Mac) - Save strategy
- Autocomplete triggers automatically as you type

### Running a Backtest

1. Configure your backtest in the right panel
2. Click "Run Backtest" button
3. View results in the Overview, Charts, or Trades tabs

## Project Structure

```
web/
├── src/
│   ├── api/               # API client (mock for now)
│   ├── components/        # React components
│   ├── editor/            # Monaco editor configuration
│   ├── pages/             # Page components
│   ├── store/             # State management
│   ├── types/             # TypeScript types
│   └── App.tsx
├── public/
│   └── examples/          # Example strategies
└── package.json
```

## Key Metrics Explained

- **Sharpe Ratio**: Risk-adjusted return (>1 is good, >2 is excellent)
- **Max Drawdown**: Largest peak-to-trough decline
- **Win Rate**: Percentage of profitable trades
- **Profit Factor**: Gross profit / gross loss (>1 means profitable)

## Development

Built by Agent 4 as part of the Canopy MVP multi-agent development workflow.

For backend integration, see Agent 5's FastAPI implementation.
