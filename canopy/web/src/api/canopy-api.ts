// Mock API client for Canopy backend
// This will be replaced with real API calls when Agent 5 builds the FastAPI backend

import type {
  BacktestConfig,
  BacktestResult,
  Strategy,
  ExampleStrategy,
  Indicator,
  PerformanceMetrics,
  Trade,
  EquityPoint,
} from '../types/canopy.types';

// Simulate network delay
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Mock data generators
const generateMockTrades = (count: number = 50): Trade[] => {
  const trades: Trade[] = [];
  let date = new Date('2023-01-01');

  for (let i = 0; i < count; i++) {
    const isBuy = i % 2 === 0;
    const price = 150 + Math.random() * 50;
    const quantity = Math.floor(Math.random() * 100) + 1;
    const pnl = isBuy ? 0 : (Math.random() - 0.4) * 1000;

    trades.push({
      id: `trade-${i}`,
      type: isBuy ? 'buy' : 'sell',
      date: date.toISOString(),
      price,
      quantity,
      pnl: isBuy ? undefined : pnl,
      pnlPercent: isBuy ? undefined : (pnl / (price * quantity)) * 100,
      commission: price * quantity * 0.001,
    });

    date.setDate(date.getDate() + Math.floor(Math.random() * 7) + 1);
  }

  return trades;
};

const generateMockEquityCurve = (count: number = 252): EquityPoint[] => {
  const points: EquityPoint[] = [];
  let equity = 100000;
  let maxEquity = equity;
  let date = new Date('2023-01-01');

  for (let i = 0; i < count; i++) {
    const change = (Math.random() - 0.47) * 500;
    equity += change;
    maxEquity = Math.max(maxEquity, equity);
    const drawdown = ((equity - maxEquity) / maxEquity) * 100;

    points.push({
      date: date.toISOString().split('T')[0],
      equity,
      drawdown,
    });

    date.setDate(date.getDate() + 1);
  }

  return points;
};

const generateMockMetrics = (): PerformanceMetrics => {
  const totalReturn = Math.random() * 20000 - 5000;
  const initialCapital = 100000;
  const winningTrades = Math.floor(Math.random() * 15) + 10;
  const losingTrades = Math.floor(Math.random() * 10) + 5;
  const totalTrades = winningTrades + losingTrades;

  return {
    totalReturn,
    totalReturnPercent: (totalReturn / initialCapital) * 100,
    sharpeRatio: Math.random() * 2 + 0.5,
    maxDrawdown: Math.random() * 15000 + 5000,
    maxDrawdownPercent: Math.random() * 15 + 5,
    winRate: (winningTrades / totalTrades) * 100,
    profitFactor: (Math.random() * 1.5) + 1,
    totalTrades,
    winningTrades,
    losingTrades,
    avgWin: Math.random() * 800 + 200,
    avgLoss: Math.random() * 500 + 100,
    largestWin: Math.random() * 2000 + 1000,
    largestLoss: Math.random() * 1500 + 500,
    avgTradeDuration: Math.random() * 10 + 2,
    expectancy: (Math.random() * 200) - 50,
    sortinoRatio: Math.random() * 2 + 0.5,
    calmarRatio: Math.random() * 1.5 + 0.3,
  };
};

// Mock API functions
export const canopyAPI = {
  // Backtest a strategy
  runBacktest: async (
    _strategyCode: string,
    config: BacktestConfig
  ): Promise<BacktestResult> => {
    console.log('Running backtest with config:', config);
    await delay(2000); // Simulate processing time

    const result: BacktestResult = {
      id: `backtest-${Date.now()}`,
      strategyId: `strategy-${Date.now()}`,
      config,
      metrics: generateMockMetrics(),
      trades: generateMockTrades(),
      equityCurve: generateMockEquityCurve(),
      startedAt: new Date().toISOString(),
      completedAt: new Date().toISOString(),
      status: 'completed',
    };

    return result;
  },

  // Get available indicators
  getIndicators: async (): Promise<Indicator[]> => {
    await delay(500);

    return [
      {
        id: 'sma',
        name: 'Simple Moving Average',
        description: 'Calculates the average price over a specified period',
        category: 'trend',
        syntax: 'sma(source, period)',
        parameters: [
          { name: 'source', type: 'number', description: 'Price source (e.g., close)', required: true },
          { name: 'period', type: 'number', description: 'Number of bars to average', required: true, default: 20 },
        ],
        example: 'fast_ma = sma(close, 10)',
      },
      {
        id: 'ema',
        name: 'Exponential Moving Average',
        description: 'Calculates exponentially weighted moving average',
        category: 'trend',
        syntax: 'ema(source, period)',
        parameters: [
          { name: 'source', type: 'number', description: 'Price source', required: true },
          { name: 'period', type: 'number', description: 'Number of bars', required: true, default: 20 },
        ],
        example: 'trend = ema(close, 50)',
      },
      {
        id: 'rsi',
        name: 'Relative Strength Index',
        description: 'Momentum oscillator measuring speed and magnitude of price changes',
        category: 'momentum',
        syntax: 'rsi(source, period)',
        parameters: [
          { name: 'source', type: 'number', description: 'Price source', required: true },
          { name: 'period', type: 'number', description: 'Lookback period', required: true, default: 14 },
        ],
        example: 'rsi_value = rsi(close, 14)',
      },
      {
        id: 'macd',
        name: 'MACD',
        description: 'Moving Average Convergence Divergence indicator',
        category: 'momentum',
        syntax: 'macd(source, fast, slow, signal)',
        parameters: [
          { name: 'source', type: 'number', description: 'Price source', required: true },
          { name: 'fast', type: 'number', description: 'Fast period', required: true, default: 12 },
          { name: 'slow', type: 'number', description: 'Slow period', required: true, default: 26 },
          { name: 'signal', type: 'number', description: 'Signal period', required: true, default: 9 },
        ],
        example: 'macd_line = macd(close, 12, 26, 9)',
      },
      {
        id: 'bbands',
        name: 'Bollinger Bands',
        description: 'Volatility bands placed above and below a moving average',
        category: 'volatility',
        syntax: 'bbands(source, period, stddev)',
        parameters: [
          { name: 'source', type: 'number', description: 'Price source', required: true },
          { name: 'period', type: 'number', description: 'MA period', required: true, default: 20 },
          { name: 'stddev', type: 'number', description: 'Standard deviations', required: true, default: 2 },
        ],
        example: 'bb_upper, bb_middle, bb_lower = bbands(close, 20, 2)',
      },
      {
        id: 'atr',
        name: 'Average True Range',
        description: 'Measures market volatility',
        category: 'volatility',
        syntax: 'atr(period)',
        parameters: [
          { name: 'period', type: 'number', description: 'Lookback period', required: true, default: 14 },
        ],
        example: 'volatility = atr(14)',
      },
    ];
  },

  // Get example strategies
  getExampleStrategies: async (): Promise<ExampleStrategy[]> => {
    await delay(500);

    return [
      {
        id: 'ma-crossover',
        name: 'Moving Average Crossover',
        description: 'Classic trend-following strategy using fast and slow moving averages',
        difficulty: 'beginner',
        category: 'trend-following',
        code: `strategy "MA Crossover"

// Define moving averages
fast_ma = sma(close, 10)
slow_ma = sma(close, 30)

// Entry: Fast MA crosses above Slow MA
buy when crossover(fast_ma, slow_ma)

// Exit: Fast MA crosses below Slow MA
sell when crossunder(fast_ma, slow_ma)

// Plot indicators
plot fast_ma
plot slow_ma
`,
      },
      {
        id: 'rsi-oversold',
        name: 'RSI Mean Reversion',
        description: 'Buy oversold conditions and sell overbought using RSI',
        difficulty: 'beginner',
        category: 'mean-reversion',
        code: `strategy "RSI Mean Reversion"

// Calculate RSI
rsi_value = rsi(close, 14)

// Entry: RSI below 30 (oversold)
buy when rsi_value < 30

// Exit: RSI above 70 (overbought)
sell when rsi_value > 70

// Plot RSI
plot rsi_value
`,
      },
      {
        id: 'bollinger-breakout',
        name: 'Bollinger Band Breakout',
        description: 'Trade breakouts from Bollinger Bands with volatility confirmation',
        difficulty: 'intermediate',
        category: 'breakout',
        code: `strategy "Bollinger Breakout"

// Calculate Bollinger Bands
bb_upper, bb_middle, bb_lower = bbands(close, 20, 2)

// Calculate ATR for volatility filter
volatility = atr(14)
avg_volatility = sma(volatility, 20)

// Entry: Price breaks above upper band with high volatility
buy when crossover(close, bb_upper) and volatility > avg_volatility

// Exit: Price touches middle band
sell when close <= bb_middle

// Plot bands
plot bb_upper
plot bb_middle
plot bb_lower
`,
      },
      {
        id: 'macd-momentum',
        name: 'MACD Momentum',
        description: 'Trade momentum shifts using MACD crossovers',
        difficulty: 'intermediate',
        category: 'momentum',
        code: `strategy "MACD Momentum"

// Calculate MACD
macd_line, signal_line, histogram = macd(close, 12, 26, 9)

// Entry: MACD crosses above signal line
buy when crossover(macd_line, signal_line) and histogram > 0

// Exit: MACD crosses below signal line
sell when crossunder(macd_line, signal_line)

// Plot MACD
plot macd_line
plot signal_line
`,
      },
    ];
  },

  // Save a strategy
  saveStrategy: async (strategy: Strategy): Promise<Strategy> => {
    await delay(500);
    console.log('Saving strategy:', strategy);
    return strategy;
  },

  // Load a strategy
  loadStrategy: async (strategyId: string): Promise<Strategy> => {
    await delay(500);
    return {
      id: strategyId,
      name: 'Loaded Strategy',
      description: 'A previously saved strategy',
      code: `strategy "Loaded Strategy"\n\nfast_ma = sma(close, 10)\nslow_ma = sma(close, 30)\n\nbuy when crossover(fast_ma, slow_ma)\nsell when crossunder(fast_ma, slow_ma)`,
      createdAt: '2024-01-01T00:00:00Z',
      updatedAt: '2024-01-01T00:00:00Z',
    };
  },

  // Validate strategy syntax
  validateStrategy: async (code: string): Promise<{ valid: boolean; errors: string[] }> => {
    await delay(300);

    // Simple mock validation
    const errors: string[] = [];

    if (!code.includes('strategy')) {
      errors.push('Strategy must start with "strategy" declaration');
    }

    if (!code.includes('buy') && !code.includes('sell')) {
      errors.push('Strategy must include at least one buy or sell signal');
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  },
};
