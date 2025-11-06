import { Link } from 'react-router-dom';
import { useCanopyStore } from '../store/useCanopyStore';

export const Home = () => {
  const { backtestHistory } = useCanopyStore();

  const features = [
    {
      icon: (
        <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"
          />
        </svg>
      ),
      title: 'Monaco Editor',
      description: 'VS Code-powered editor with syntax highlighting and autocomplete',
    },
    {
      icon: (
        <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M13 10V3L4 14h7v7l9-11h-7z"
          />
        </svg>
      ),
      title: 'Built-in Indicators',
      description: 'Access to SMA, EMA, RSI, MACD, Bollinger Bands, and more',
    },
    {
      icon: (
        <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
          />
        </svg>
      ),
      title: 'Performance Analytics',
      description: 'Detailed metrics including Sharpe ratio, drawdown, win rate, and more',
    },
    {
      icon: (
        <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"
          />
        </svg>
      ),
      title: 'Interactive Charts',
      description: 'Visualize equity curves, drawdowns, and trade performance',
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-white mb-4">
            Welcome to <span className="text-canopy-400">Canopy IDE</span>
          </h1>
          <p className="text-xl text-gray-400 mb-8 max-w-2xl mx-auto">
            A modern web-based IDE for developing and backtesting algorithmic trading strategies
            with an intuitive domain-specific language.
          </p>
          <div className="flex gap-4 justify-center">
            <Link
              to="/editor"
              className="px-6 py-3 bg-canopy-600 hover:bg-canopy-700 text-white font-medium rounded-lg transition-colors flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                />
              </svg>
              Start Coding
            </Link>
            <a
              href="https://github.com/canopy-lang"
              target="_blank"
              rel="noopener noreferrer"
              className="px-6 py-3 bg-gray-800 hover:bg-gray-700 text-white font-medium rounded-lg transition-colors flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path
                  fillRule="evenodd"
                  d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
                  clipRule="evenodd"
                />
              </svg>
              View on GitHub
            </a>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
          {features.map((feature, index) => (
            <div
              key={index}
              className="bg-gray-800 border border-gray-700 rounded-lg p-6 hover:border-canopy-500 transition-colors"
            >
              <div className="text-canopy-400 mb-4">{feature.icon}</div>
              <h3 className="text-lg font-semibold text-white mb-2">{feature.title}</h3>
              <p className="text-sm text-gray-400">{feature.description}</p>
            </div>
          ))}
        </div>

        {/* Recent Activity */}
        {backtestHistory.length > 0 && (
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-white mb-4">Recent Backtests</h2>
            <div className="space-y-3">
              {backtestHistory.slice(0, 5).map((backtest) => (
                <div
                  key={backtest.id}
                  className="flex items-center justify-between p-4 bg-gray-900 rounded border border-gray-700"
                >
                  <div>
                    <div className="text-sm font-medium text-gray-200">
                      {backtest.config.symbol}
                    </div>
                    <div className="text-xs text-gray-500">
                      {new Date(backtest.completedAt).toLocaleDateString()}
                    </div>
                  </div>
                  <div className="text-right">
                    <div
                      className={`text-sm font-medium ${
                        backtest.metrics.totalReturn > 0 ? 'text-green-400' : 'text-red-400'
                      }`}
                    >
                      {backtest.metrics.totalReturn > 0 ? '+' : ''}
                      {backtest.metrics.totalReturnPercent.toFixed(2)}%
                    </div>
                    <div className="text-xs text-gray-500">
                      Sharpe: {backtest.metrics.sharpeRatio.toFixed(2)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Quick Start */}
        <div className="mt-16 bg-gray-800 border border-gray-700 rounded-lg p-8">
          <h2 className="text-2xl font-semibold text-white mb-4">Quick Start</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div>
              <div className="w-10 h-10 bg-canopy-600 rounded-full flex items-center justify-center text-white font-bold mb-3">
                1
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Write Strategy</h3>
              <p className="text-sm text-gray-400">
                Use our intuitive DSL to define your trading logic with built-in indicators
              </p>
            </div>
            <div>
              <div className="w-10 h-10 bg-canopy-600 rounded-full flex items-center justify-center text-white font-bold mb-3">
                2
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Configure Backtest</h3>
              <p className="text-sm text-gray-400">
                Set your symbol, date range, capital, and other parameters
              </p>
            </div>
            <div>
              <div className="w-10 h-10 bg-canopy-600 rounded-full flex items-center justify-center text-white font-bold mb-3">
                3
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Analyze Results</h3>
              <p className="text-sm text-gray-400">
                Review detailed metrics, charts, and trade-by-trade performance
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
