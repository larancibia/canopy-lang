// TypeScript type definitions for Canopy

export interface Strategy {
  id: string;
  name: string;
  description: string;
  code: string;
  author?: string;
  createdAt: string;
  updatedAt: string;
}

export interface BacktestConfig {
  symbol: string;
  startDate: string;
  endDate: string;
  initialCapital: number;
  commission?: number;
  slippage?: number;
}

export interface Trade {
  id: string;
  type: 'buy' | 'sell';
  date: string;
  price: number;
  quantity: number;
  pnl?: number;
  pnlPercent?: number;
  commission?: number;
}

export interface PerformanceMetrics {
  totalReturn: number;
  totalReturnPercent: number;
  sharpeRatio: number;
  maxDrawdown: number;
  maxDrawdownPercent: number;
  winRate: number;
  profitFactor: number;
  totalTrades: number;
  winningTrades: number;
  losingTrades: number;
  avgWin: number;
  avgLoss: number;
  largestWin: number;
  largestLoss: number;
  avgTradeDuration: number;
  expectancy: number;
  sortinoRatio?: number;
  calmarRatio?: number;
}

export interface EquityPoint {
  date: string;
  equity: number;
  drawdown: number;
}

export interface BacktestResult {
  id: string;
  strategyId: string;
  config: BacktestConfig;
  metrics: PerformanceMetrics;
  trades: Trade[];
  equityCurve: EquityPoint[];
  startedAt: string;
  completedAt: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  error?: string;
}

export interface Indicator {
  id: string;
  name: string;
  description: string;
  category: 'trend' | 'momentum' | 'volatility' | 'volume' | 'custom';
  syntax: string;
  parameters: IndicatorParameter[];
  example: string;
}

export interface IndicatorParameter {
  name: string;
  type: 'number' | 'string' | 'boolean';
  description: string;
  default?: any;
  required: boolean;
}

export interface ExampleStrategy {
  id: string;
  name: string;
  description: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  category: 'trend-following' | 'mean-reversion' | 'momentum' | 'breakout' | 'custom';
  code: string;
  expectedMetrics?: Partial<PerformanceMetrics>;
}

export interface EditorTheme {
  name: string;
  isDark: boolean;
}

export interface UIPreferences {
  theme: 'light' | 'dark';
  editorTheme: string;
  fontSize: number;
  showMinimap: boolean;
  showLineNumbers: boolean;
  wordWrap: boolean;
}
