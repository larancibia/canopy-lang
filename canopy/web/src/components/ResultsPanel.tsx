import { useState } from 'react';
import { useCanopyStore } from '../store/useCanopyStore';
import { MetricsTable } from './MetricsTable';
import { EquityCurveChart } from './EquityCurveChart';

export const ResultsPanel = () => {
  const { currentBacktest } = useCanopyStore();
  const [selectedView, setSelectedView] = useState<'overview' | 'trades' | 'charts'>('overview');

  if (!currentBacktest) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-900">
        <div className="text-center">
          <svg
            className="w-16 h-16 mx-auto text-gray-700 mb-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
            />
          </svg>
          <h3 className="text-lg font-medium text-gray-400 mb-2">No Results Yet</h3>
          <p className="text-sm text-gray-500">Run a backtest to see results here</p>
        </div>
      </div>
    );
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(value);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <div className="h-full flex flex-col bg-gray-900">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 px-4 py-3">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-gray-200">Backtest Results</h3>
            <p className="text-xs text-gray-500 mt-0.5">
              {currentBacktest.config.symbol} • {formatDate(currentBacktest.config.startDate)} to{' '}
              {formatDate(currentBacktest.config.endDate)}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span
              className={`px-2 py-1 text-xs font-medium rounded ${
                currentBacktest.metrics.totalReturn > 0
                  ? 'bg-green-900/30 text-green-400'
                  : 'bg-red-900/30 text-red-400'
              }`}
            >
              {currentBacktest.metrics.totalReturn > 0 ? '+' : ''}
              {formatCurrency(currentBacktest.metrics.totalReturn)}
            </span>
          </div>
        </div>
      </div>

      {/* View Tabs */}
      <div className="bg-gray-800 border-b border-gray-700 px-4">
        <div className="flex gap-1">
          {[
            { id: 'overview', label: 'Overview' },
            { id: 'charts', label: 'Charts' },
            { id: 'trades', label: 'Trades' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setSelectedView(tab.id as any)}
              className={`px-4 py-2 text-sm font-medium transition-colors border-b-2 ${
                selectedView === tab.id
                  ? 'text-canopy-400 border-canopy-500'
                  : 'text-gray-400 border-transparent hover:text-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {selectedView === 'overview' && (
          <div>
            <MetricsTable metrics={currentBacktest.metrics} />
          </div>
        )}

        {selectedView === 'charts' && (
          <div>
            <EquityCurveChart data={currentBacktest.equityCurve} />
          </div>
        )}

        {selectedView === 'trades' && (
          <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-900 border-b border-gray-700">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Price
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Quantity
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">
                      Commission
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">
                      P&L
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">
                      P&L %
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-700">
                  {currentBacktest.trades.map((trade) => (
                    <tr key={trade.id} className="hover:bg-gray-800/50">
                      <td className="px-4 py-3 whitespace-nowrap text-gray-300">
                        {formatDate(trade.date)}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap">
                        <span
                          className={`px-2 py-1 text-xs font-medium rounded ${
                            trade.type === 'buy'
                              ? 'bg-blue-900/30 text-blue-400'
                              : 'bg-purple-900/30 text-purple-400'
                          }`}
                        >
                          {trade.type.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-right text-gray-300">
                        {formatCurrency(trade.price)}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-right text-gray-300">
                        {trade.quantity}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-right text-gray-400">
                        {formatCurrency(trade.commission || 0)}
                      </td>
                      <td
                        className={`px-4 py-3 whitespace-nowrap text-right font-medium ${
                          trade.pnl
                            ? trade.pnl > 0
                              ? 'text-green-400'
                              : 'text-red-400'
                            : 'text-gray-500'
                        }`}
                      >
                        {trade.pnl ? formatCurrency(trade.pnl) : '-'}
                      </td>
                      <td
                        className={`px-4 py-3 whitespace-nowrap text-right font-medium ${
                          trade.pnlPercent
                            ? trade.pnlPercent > 0
                              ? 'text-green-400'
                              : 'text-red-400'
                            : 'text-gray-500'
                        }`}
                      >
                        {trade.pnlPercent ? `${trade.pnlPercent.toFixed(2)}%` : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
