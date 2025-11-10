import type { PerformanceMetrics } from '../types/canopy.types';

interface MetricsTableProps {
  metrics: PerformanceMetrics;
}

export const MetricsTable = ({ metrics }: MetricsTableProps) => {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(value);
  };

  const formatPercent = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  const formatNumber = (value: number, decimals: number = 2) => {
    return value.toFixed(decimals);
  };

  const metricGroups = [
    {
      title: 'Returns',
      metrics: [
        { label: 'Total Return', value: formatCurrency(metrics.totalReturn), positive: metrics.totalReturn > 0 },
        { label: 'Total Return %', value: formatPercent(metrics.totalReturnPercent), positive: metrics.totalReturnPercent > 0 },
        { label: 'Sharpe Ratio', value: formatNumber(metrics.sharpeRatio), positive: metrics.sharpeRatio > 1 },
        { label: 'Sortino Ratio', value: metrics.sortinoRatio ? formatNumber(metrics.sortinoRatio) : 'N/A', positive: (metrics.sortinoRatio || 0) > 1 },
      ],
    },
    {
      title: 'Risk',
      metrics: [
        { label: 'Max Drawdown', value: formatCurrency(metrics.maxDrawdown), positive: false },
        { label: 'Max Drawdown %', value: formatPercent(-metrics.maxDrawdownPercent), positive: false },
        { label: 'Calmar Ratio', value: metrics.calmarRatio ? formatNumber(metrics.calmarRatio) : 'N/A', positive: (metrics.calmarRatio || 0) > 1 },
      ],
    },
    {
      title: 'Trading',
      metrics: [
        { label: 'Total Trades', value: metrics.totalTrades.toString(), positive: null },
        { label: 'Winning Trades', value: metrics.winningTrades.toString(), positive: null },
        { label: 'Losing Trades', value: metrics.losingTrades.toString(), positive: null },
        { label: 'Win Rate', value: formatPercent(metrics.winRate), positive: metrics.winRate > 50 },
        { label: 'Profit Factor', value: formatNumber(metrics.profitFactor), positive: metrics.profitFactor > 1 },
      ],
    },
    {
      title: 'Trade Analysis',
      metrics: [
        { label: 'Avg Win', value: formatCurrency(metrics.avgWin), positive: true },
        { label: 'Avg Loss', value: formatCurrency(metrics.avgLoss), positive: false },
        { label: 'Largest Win', value: formatCurrency(metrics.largestWin), positive: true },
        { label: 'Largest Loss', value: formatCurrency(metrics.largestLoss), positive: false },
        { label: 'Avg Trade Duration', value: `${formatNumber(metrics.avgTradeDuration, 1)} days`, positive: null },
        { label: 'Expectancy', value: formatCurrency(metrics.expectancy), positive: metrics.expectancy > 0 },
      ],
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {metricGroups.map((group) => (
        <div key={group.title} className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h4 className="text-sm font-semibold text-gray-300 mb-3 pb-2 border-b border-gray-700">
            {group.title}
          </h4>
          <div className="space-y-2">
            {group.metrics.map((metric) => (
              <div key={metric.label} className="flex justify-between items-center">
                <span className="text-xs text-gray-400">{metric.label}</span>
                <span
                  className={`text-sm font-medium ${
                    metric.positive === true
                      ? 'text-green-400'
                      : metric.positive === false
                      ? 'text-red-400'
                      : 'text-gray-200'
                  }`}
                >
                  {metric.value}
                </span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};
