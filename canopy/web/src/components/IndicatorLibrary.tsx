import { useState, useEffect } from 'react';
import { canopyAPI } from '../api/canopy-api';
import type { Indicator } from '../types/canopy.types';
import { useCanopyStore } from '../store/useCanopyStore';

export const IndicatorLibrary = () => {
  const [indicators, setIndicators] = useState<Indicator[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedIndicator, setSelectedIndicator] = useState<Indicator | null>(null);
  const { setEditorContent, editorContent } = useCanopyStore();

  useEffect(() => {
    loadIndicators();
  }, []);

  const loadIndicators = async () => {
    setLoading(true);
    try {
      const data = await canopyAPI.getIndicators();
      setIndicators(data);
    } catch (error) {
      console.error('Failed to load indicators:', error);
    } finally {
      setLoading(false);
    }
  };

  const categories = [
    { id: 'all', label: 'All Indicators' },
    { id: 'trend', label: 'Trend' },
    { id: 'momentum', label: 'Momentum' },
    { id: 'volatility', label: 'Volatility' },
    { id: 'volume', label: 'Volume' },
  ];

  const filteredIndicators = indicators.filter((indicator) => {
    const matchesSearch =
      indicator.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      indicator.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || indicator.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const insertIndicator = (indicator: Indicator) => {
    const insertion = `\n${indicator.example}\n`;
    setEditorContent(editorContent + insertion);
  };

  return (
    <div className="h-full flex bg-gray-900">
      {/* Indicator List */}
      <div className="w-80 border-r border-gray-700 flex flex-col">
        {/* Header */}
        <div className="bg-gray-800 border-b border-gray-700 px-4 py-3">
          <h3 className="text-sm font-semibold text-gray-200">Indicator Library</h3>
        </div>

        {/* Search */}
        <div className="p-3 border-b border-gray-700">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search indicators..."
            className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-gray-200 text-sm focus:outline-none focus:border-canopy-500"
          />
        </div>

        {/* Category Filter */}
        <div className="flex gap-1 px-3 py-2 border-b border-gray-700 overflow-x-auto">
          {categories.map((category) => (
            <button
              key={category.id}
              onClick={() => setSelectedCategory(category.id)}
              className={`px-3 py-1 text-xs font-medium rounded whitespace-nowrap transition-colors ${
                selectedCategory === category.id
                  ? 'bg-canopy-600 text-white'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
            >
              {category.label}
            </button>
          ))}
        </div>

        {/* Indicator List */}
        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="flex items-center justify-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-canopy-500"></div>
            </div>
          ) : filteredIndicators.length === 0 ? (
            <div className="p-4 text-center text-sm text-gray-500">No indicators found</div>
          ) : (
            <div className="divide-y divide-gray-700">
              {filteredIndicators.map((indicator) => (
                <button
                  key={indicator.id}
                  onClick={() => setSelectedIndicator(indicator)}
                  className={`w-full text-left px-4 py-3 hover:bg-gray-800 transition-colors ${
                    selectedIndicator?.id === indicator.id ? 'bg-gray-800' : ''
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <h4 className="text-sm font-medium text-gray-200">{indicator.name}</h4>
                      <p className="text-xs text-gray-500 mt-0.5 line-clamp-2">
                        {indicator.description}
                      </p>
                    </div>
                    <span
                      className={`px-2 py-0.5 text-xs rounded whitespace-nowrap ${
                        indicator.category === 'trend'
                          ? 'bg-blue-900/30 text-blue-400'
                          : indicator.category === 'momentum'
                          ? 'bg-purple-900/30 text-purple-400'
                          : indicator.category === 'volatility'
                          ? 'bg-orange-900/30 text-orange-400'
                          : 'bg-green-900/30 text-green-400'
                      }`}
                    >
                      {indicator.category}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Indicator Detail */}
      <div className="flex-1 flex flex-col">
        {selectedIndicator ? (
          <>
            {/* Detail Header */}
            <div className="bg-gray-800 border-b border-gray-700 px-6 py-4">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-gray-200">
                    {selectedIndicator.name}
                  </h3>
                  <p className="text-sm text-gray-400 mt-1">{selectedIndicator.description}</p>
                </div>
                <button
                  onClick={() => insertIndicator(selectedIndicator)}
                  className="px-4 py-2 bg-canopy-600 hover:bg-canopy-700 text-white text-sm rounded transition-colors flex items-center gap-2"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 4v16m8-8H4"
                    />
                  </svg>
                  Insert Code
                </button>
              </div>
            </div>

            {/* Detail Content */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {/* Syntax */}
              <div>
                <h4 className="text-sm font-semibold text-gray-300 mb-2">Syntax</h4>
                <div className="bg-gray-800 border border-gray-700 rounded p-3">
                  <code className="text-sm text-canopy-400 font-mono">
                    {selectedIndicator.syntax}
                  </code>
                </div>
              </div>

              {/* Parameters */}
              <div>
                <h4 className="text-sm font-semibold text-gray-300 mb-2">Parameters</h4>
                <div className="bg-gray-800 border border-gray-700 rounded overflow-hidden">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-900 border-b border-gray-700">
                      <tr>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-400">
                          Name
                        </th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-400">
                          Type
                        </th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-400">
                          Required
                        </th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-400">
                          Default
                        </th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-400">
                          Description
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-700">
                      {selectedIndicator.parameters.map((param) => (
                        <tr key={param.name}>
                          <td className="px-4 py-2 font-mono text-canopy-400">{param.name}</td>
                          <td className="px-4 py-2 text-gray-400">{param.type}</td>
                          <td className="px-4 py-2">
                            <span
                              className={`px-2 py-0.5 text-xs rounded ${
                                param.required
                                  ? 'bg-red-900/30 text-red-400'
                                  : 'bg-gray-700 text-gray-400'
                              }`}
                            >
                              {param.required ? 'Required' : 'Optional'}
                            </span>
                          </td>
                          <td className="px-4 py-2 font-mono text-gray-400">
                            {param.default !== undefined ? String(param.default) : '-'}
                          </td>
                          <td className="px-4 py-2 text-gray-400">{param.description}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Example */}
              <div>
                <h4 className="text-sm font-semibold text-gray-300 mb-2">Example</h4>
                <div className="bg-gray-800 border border-gray-700 rounded p-4">
                  <pre className="text-sm text-gray-300 font-mono">{selectedIndicator.example}</pre>
                </div>
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
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
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
              <h3 className="text-lg font-medium text-gray-400 mb-2">Select an Indicator</h3>
              <p className="text-sm text-gray-500">Choose an indicator to view details</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
