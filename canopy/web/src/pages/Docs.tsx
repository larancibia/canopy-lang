export const Docs = () => {
  return (
    <div className="min-h-screen bg-gray-900">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-4">Canopy Documentation</h1>
          <p className="text-lg text-gray-400">
            Learn how to write trading strategies with the Canopy domain-specific language
          </p>
        </div>

        {/* Content */}
        <div className="space-y-8">
          {/* Getting Started */}
          <section className="bg-gray-800 border border-gray-700 rounded-lg p-6">
            <h2 className="text-2xl font-semibold text-white mb-4">Getting Started</h2>
            <p className="text-gray-300 mb-4">
              Canopy is a domain-specific language designed to make algorithmic trading strategy
              development simple and intuitive. Here's a basic example:
            </p>
            <div className="bg-gray-900 border border-gray-700 rounded p-4">
              <pre className="text-sm text-gray-300 font-mono">
{`strategy "My First Strategy"

// Calculate moving averages
fast_ma = sma(close, 10)
slow_ma = sma(close, 30)

// Buy when fast crosses above slow
buy when crossover(fast_ma, slow_ma)

// Sell when fast crosses below slow
sell when crossunder(fast_ma, slow_ma)

// Plot the indicators
plot fast_ma
plot slow_ma`}
              </pre>
            </div>
          </section>

          {/* Language Syntax */}
          <section className="bg-gray-800 border border-gray-700 rounded-lg p-6">
            <h2 className="text-2xl font-semibold text-white mb-4">Language Syntax</h2>

            <h3 className="text-lg font-semibold text-white mt-4 mb-2">Strategy Declaration</h3>
            <p className="text-gray-300 mb-2">Every strategy must start with a strategy name:</p>
            <div className="bg-gray-900 border border-gray-700 rounded p-3 mb-4">
              <code className="text-sm text-canopy-400 font-mono">strategy "Strategy Name"</code>
            </div>

            <h3 className="text-lg font-semibold text-white mt-4 mb-2">Variables</h3>
            <p className="text-gray-300 mb-2">Assign values to variables using the equals sign:</p>
            <div className="bg-gray-900 border border-gray-700 rounded p-3 mb-4">
              <code className="text-sm text-canopy-400 font-mono">
                variable_name = sma(close, 20)
              </code>
            </div>

            <h3 className="text-lg font-semibold text-white mt-4 mb-2">Buy/Sell Signals</h3>
            <p className="text-gray-300 mb-2">Define entry and exit conditions:</p>
            <div className="bg-gray-900 border border-gray-700 rounded p-3 mb-4">
              <pre className="text-sm text-canopy-400 font-mono">
{`buy when condition
sell when condition`}
              </pre>
            </div>

            <h3 className="text-lg font-semibold text-white mt-4 mb-2">Comments</h3>
            <p className="text-gray-300 mb-2">Use // for single-line comments:</p>
            <div className="bg-gray-900 border border-gray-700 rounded p-3 mb-4">
              <code className="text-sm text-gray-500 font-mono">// This is a comment</code>
            </div>
          </section>

          {/* Built-in Variables */}
          <section className="bg-gray-800 border border-gray-700 rounded-lg p-6">
            <h2 className="text-2xl font-semibold text-white mb-4">Built-in Variables</h2>
            <div className="space-y-2">
              {[
                { name: 'close', desc: 'Closing price' },
                { name: 'open', desc: 'Opening price' },
                { name: 'high', desc: 'High price' },
                { name: 'low', desc: 'Low price' },
                { name: 'volume', desc: 'Trading volume' },
              ].map((item) => (
                <div key={item.name} className="flex items-start gap-3">
                  <code className="text-sm text-canopy-400 font-mono min-w-[100px]">
                    {item.name}
                  </code>
                  <span className="text-sm text-gray-400">{item.desc}</span>
                </div>
              ))}
            </div>
          </section>

          {/* Indicators */}
          <section className="bg-gray-800 border border-gray-700 rounded-lg p-6">
            <h2 className="text-2xl font-semibold text-white mb-4">Indicators</h2>

            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-semibold text-white mb-2">
                  sma(source, period) - Simple Moving Average
                </h3>
                <p className="text-gray-400 text-sm mb-2">
                  Calculates the average price over a specified period
                </p>
                <div className="bg-gray-900 border border-gray-700 rounded p-3">
                  <code className="text-sm text-canopy-400 font-mono">ma20 = sma(close, 20)</code>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-white mb-2">
                  ema(source, period) - Exponential Moving Average
                </h3>
                <p className="text-gray-400 text-sm mb-2">
                  Calculates exponentially weighted moving average
                </p>
                <div className="bg-gray-900 border border-gray-700 rounded p-3">
                  <code className="text-sm text-canopy-400 font-mono">ema20 = ema(close, 20)</code>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-white mb-2">
                  rsi(source, period) - Relative Strength Index
                </h3>
                <p className="text-gray-400 text-sm mb-2">
                  Momentum oscillator measuring speed and magnitude of price changes
                </p>
                <div className="bg-gray-900 border border-gray-700 rounded p-3">
                  <code className="text-sm text-canopy-400 font-mono">rsi_val = rsi(close, 14)</code>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-white mb-2">
                  macd(source, fast, slow, signal) - MACD
                </h3>
                <p className="text-gray-400 text-sm mb-2">
                  Moving Average Convergence Divergence indicator
                </p>
                <div className="bg-gray-900 border border-gray-700 rounded p-3">
                  <code className="text-sm text-canopy-400 font-mono">
                    macd_line = macd(close, 12, 26, 9)
                  </code>
                </div>
              </div>
            </div>
          </section>

          {/* Functions */}
          <section className="bg-gray-800 border border-gray-700 rounded-lg p-6">
            <h2 className="text-2xl font-semibold text-white mb-4">Functions</h2>

            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-semibold text-white mb-2">
                  crossover(series1, series2)
                </h3>
                <p className="text-gray-400 text-sm mb-2">
                  Returns true when series1 crosses above series2
                </p>
                <div className="bg-gray-900 border border-gray-700 rounded p-3">
                  <code className="text-sm text-canopy-400 font-mono">
                    buy when crossover(fast_ma, slow_ma)
                  </code>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-white mb-2">
                  crossunder(series1, series2)
                </h3>
                <p className="text-gray-400 text-sm mb-2">
                  Returns true when series1 crosses below series2
                </p>
                <div className="bg-gray-900 border border-gray-700 rounded p-3">
                  <code className="text-sm text-canopy-400 font-mono">
                    sell when crossunder(fast_ma, slow_ma)
                  </code>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-white mb-2">
                  highest(series, period)
                </h3>
                <p className="text-gray-400 text-sm mb-2">
                  Returns the highest value in series over the specified period
                </p>
                <div className="bg-gray-900 border border-gray-700 rounded p-3">
                  <code className="text-sm text-canopy-400 font-mono">
                    high20 = highest(close, 20)
                  </code>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-white mb-2">
                  lowest(series, period)
                </h3>
                <p className="text-gray-400 text-sm mb-2">
                  Returns the lowest value in series over the specified period
                </p>
                <div className="bg-gray-900 border border-gray-700 rounded p-3">
                  <code className="text-sm text-canopy-400 font-mono">
                    low20 = lowest(close, 20)
                  </code>
                </div>
              </div>
            </div>
          </section>

          {/* Examples */}
          <section className="bg-gray-800 border border-gray-700 rounded-lg p-6">
            <h2 className="text-2xl font-semibold text-white mb-4">Example Strategies</h2>

            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-white mb-2">RSI Mean Reversion</h3>
                <div className="bg-gray-900 border border-gray-700 rounded p-4">
                  <pre className="text-sm text-gray-300 font-mono">
{`strategy "RSI Mean Reversion"

rsi_value = rsi(close, 14)

buy when rsi_value < 30
sell when rsi_value > 70

plot rsi_value`}
                  </pre>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-white mb-2">Bollinger Band Breakout</h3>
                <div className="bg-gray-900 border border-gray-700 rounded p-4">
                  <pre className="text-sm text-gray-300 font-mono">
{`strategy "Bollinger Breakout"

bb_upper, bb_middle, bb_lower = bbands(close, 20, 2)

buy when crossover(close, bb_upper)
sell when close <= bb_middle

plot bb_upper
plot bb_middle
plot bb_lower`}
                  </pre>
                </div>
              </div>
            </div>
          </section>

          {/* Best Practices */}
          <section className="bg-gray-800 border border-gray-700 rounded-lg p-6">
            <h2 className="text-2xl font-semibold text-white mb-4">Best Practices</h2>
            <ul className="space-y-2 text-gray-300">
              <li className="flex items-start gap-2">
                <span className="text-canopy-400 mt-1">•</span>
                <span>Always test your strategy on historical data before live trading</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-canopy-400 mt-1">•</span>
                <span>Use meaningful variable names to make your code readable</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-canopy-400 mt-1">•</span>
                <span>Add comments to explain your trading logic</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-canopy-400 mt-1">•</span>
                <span>Consider multiple time frames and market conditions</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-canopy-400 mt-1">•</span>
                <span>Monitor key metrics like Sharpe ratio, drawdown, and win rate</span>
              </li>
            </ul>
          </section>
        </div>
      </div>
    </div>
  );
};
