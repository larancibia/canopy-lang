import { useState } from 'react';
import { useCanopyStore } from '../store/useCanopyStore';
import { canopyAPI } from '../api/canopy-api';

export const BacktestPanel = () => {
  const {
    backtestConfig,
    setBacktestConfig,
    editorContent,
    isBacktesting,
    setIsBacktesting,
    setCurrentBacktest,
    addBacktestToHistory,
  } = useCanopyStore();

  const [error, setError] = useState<string | null>(null);

  const handleRunBacktest = async () => {
    if (!editorContent.trim()) {
      setError('Please write a strategy before running backtest');
      return;
    }

    setError(null);
    setIsBacktesting(true);

    try {
      // Validate strategy first
      const validation = await canopyAPI.validateStrategy(editorContent);
      if (!validation.valid) {
        setError(validation.errors.join(', '));
        setIsBacktesting(false);
        return;
      }

      // Run backtest
      const result = await canopyAPI.runBacktest(editorContent, backtestConfig);
      setCurrentBacktest(result);
      addBacktestToHistory(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to run backtest');
    } finally {
      setIsBacktesting(false);
    }
  };

  return (
    <div className="h-full flex flex-col bg-gray-900">
      {/* Panel Header */}
      <div className="bg-gray-800 border-b border-gray-700 px-4 py-3">
        <h3 className="text-sm font-semibold text-gray-200">Backtest Configuration</h3>
      </div>

      {/* Configuration Form */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Symbol Input */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1.5">
            Symbol
          </label>
          <input
            type="text"
            value={backtestConfig.symbol}
            onChange={(e) => setBacktestConfig({ symbol: e.target.value.toUpperCase() })}
            className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-gray-200 text-sm focus:outline-none focus:border-canopy-500"
            placeholder="AAPL"
          />
          <p className="mt-1 text-xs text-gray-500">Stock ticker symbol</p>
        </div>

        {/* Date Range */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">
              Start Date
            </label>
            <input
              type="date"
              value={backtestConfig.startDate}
              onChange={(e) => setBacktestConfig({ startDate: e.target.value })}
              className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-gray-200 text-sm focus:outline-none focus:border-canopy-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">
              End Date
            </label>
            <input
              type="date"
              value={backtestConfig.endDate}
              onChange={(e) => setBacktestConfig({ endDate: e.target.value })}
              className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-gray-200 text-sm focus:outline-none focus:border-canopy-500"
            />
          </div>
        </div>

        {/* Initial Capital */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1.5">
            Initial Capital ($)
          </label>
          <input
            type="number"
            value={backtestConfig.initialCapital}
            onChange={(e) => setBacktestConfig({ initialCapital: Number(e.target.value) })}
            className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-gray-200 text-sm focus:outline-none focus:border-canopy-500"
            min="1000"
            step="1000"
          />
          <p className="mt-1 text-xs text-gray-500">Starting account balance</p>
        </div>

        {/* Advanced Settings */}
        <details className="group">
          <summary className="cursor-pointer text-sm font-medium text-gray-300 mb-2 flex items-center gap-2">
            <svg
              className="w-4 h-4 transition-transform group-open:rotate-90"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            Advanced Settings
          </summary>

          <div className="space-y-4 pl-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">
                Commission (%)
              </label>
              <input
                type="number"
                value={backtestConfig.commission ? backtestConfig.commission * 100 : 0.1}
                onChange={(e) => setBacktestConfig({ commission: Number(e.target.value) / 100 })}
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-gray-200 text-sm focus:outline-none focus:border-canopy-500"
                min="0"
                step="0.01"
              />
              <p className="mt-1 text-xs text-gray-500">Trading fees per transaction</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">
                Slippage (%)
              </label>
              <input
                type="number"
                value={backtestConfig.slippage ? backtestConfig.slippage * 100 : 0.05}
                onChange={(e) => setBacktestConfig({ slippage: Number(e.target.value) / 100 })}
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-gray-200 text-sm focus:outline-none focus:border-canopy-500"
                min="0"
                step="0.01"
              />
              <p className="mt-1 text-xs text-gray-500">Expected price slippage</p>
            </div>
          </div>
        </details>

        {/* Error Display */}
        {error && (
          <div className="p-3 bg-red-900/20 border border-red-700 rounded">
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}

        {/* Run Button */}
        <button
          onClick={handleRunBacktest}
          disabled={isBacktesting}
          className="w-full px-4 py-3 bg-canopy-600 hover:bg-canopy-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white font-medium rounded transition-colors flex items-center justify-center gap-2"
        >
          {isBacktesting ? (
            <>
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                  fill="none"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              Running Backtest...
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              Run Backtest
            </>
          )}
        </button>

        {/* Info Box */}
        <div className="p-3 bg-blue-900/20 border border-blue-700 rounded">
          <p className="text-xs text-blue-400">
            Backtest will simulate your strategy on historical data from {backtestConfig.startDate}{' '}
            to {backtestConfig.endDate} for {backtestConfig.symbol}.
          </p>
        </div>
      </div>
    </div>
  );
};
