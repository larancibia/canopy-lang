import { useState, useEffect } from 'react';
import { canopyAPI } from '../api/canopy-api';
import type { ExampleStrategy } from '../types/canopy.types';
import { useCanopyStore } from '../store/useCanopyStore';

export const StrategyExplorer = () => {
  const [strategies, setStrategies] = useState<ExampleStrategy[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('all');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedStrategy, setSelectedStrategy] = useState<ExampleStrategy | null>(null);
  const { setEditorContent, setUnsavedChanges } = useCanopyStore();

  useEffect(() => {
    loadStrategies();
  }, []);

  const loadStrategies = async () => {
    setLoading(true);
    try {
      const data = await canopyAPI.getExampleStrategies();
      setStrategies(data);
    } catch (error) {
      console.error('Failed to load strategies:', error);
    } finally {
      setLoading(false);
    }
  };

  const difficulties = [
    { id: 'all', label: 'All Levels' },
    { id: 'beginner', label: 'Beginner' },
    { id: 'intermediate', label: 'Intermediate' },
    { id: 'advanced', label: 'Advanced' },
  ];

  const categories = [
    { id: 'all', label: 'All Categories' },
    { id: 'trend-following', label: 'Trend Following' },
    { id: 'mean-reversion', label: 'Mean Reversion' },
    { id: 'momentum', label: 'Momentum' },
    { id: 'breakout', label: 'Breakout' },
  ];

  const filteredStrategies = strategies.filter((strategy) => {
    const matchesSearch =
      strategy.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      strategy.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesDifficulty =
      selectedDifficulty === 'all' || strategy.difficulty === selectedDifficulty;
    const matchesCategory = selectedCategory === 'all' || strategy.category === selectedCategory;
    return matchesSearch && matchesDifficulty && matchesCategory;
  });

  const loadStrategy = (strategy: ExampleStrategy) => {
    setEditorContent(strategy.code);
    setUnsavedChanges(true);
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner':
        return 'bg-green-900/30 text-green-400';
      case 'intermediate':
        return 'bg-yellow-900/30 text-yellow-400';
      case 'advanced':
        return 'bg-red-900/30 text-red-400';
      default:
        return 'bg-gray-700 text-gray-400';
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'trend-following':
        return 'bg-blue-900/30 text-blue-400';
      case 'mean-reversion':
        return 'bg-purple-900/30 text-purple-400';
      case 'momentum':
        return 'bg-pink-900/30 text-pink-400';
      case 'breakout':
        return 'bg-orange-900/30 text-orange-400';
      default:
        return 'bg-gray-700 text-gray-400';
    }
  };

  return (
    <div className="h-full flex bg-gray-900">
      {/* Strategy List */}
      <div className="w-80 border-r border-gray-700 flex flex-col">
        {/* Header */}
        <div className="bg-gray-800 border-b border-gray-700 px-4 py-3">
          <h3 className="text-sm font-semibold text-gray-200">Example Strategies</h3>
        </div>

        {/* Search */}
        <div className="p-3 border-b border-gray-700">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search strategies..."
            className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-gray-200 text-sm focus:outline-none focus:border-canopy-500"
          />
        </div>

        {/* Filters */}
        <div className="p-3 border-b border-gray-700 space-y-3">
          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1.5">Difficulty</label>
            <select
              value={selectedDifficulty}
              onChange={(e) => setSelectedDifficulty(e.target.value)}
              className="w-full px-3 py-1.5 bg-gray-800 border border-gray-700 rounded text-gray-200 text-sm focus:outline-none focus:border-canopy-500"
            >
              {difficulties.map((diff) => (
                <option key={diff.id} value={diff.id}>
                  {diff.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1.5">Category</label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full px-3 py-1.5 bg-gray-800 border border-gray-700 rounded text-gray-200 text-sm focus:outline-none focus:border-canopy-500"
            >
              {categories.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {cat.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Strategy List */}
        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="flex items-center justify-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-canopy-500"></div>
            </div>
          ) : filteredStrategies.length === 0 ? (
            <div className="p-4 text-center text-sm text-gray-500">No strategies found</div>
          ) : (
            <div className="divide-y divide-gray-700">
              {filteredStrategies.map((strategy) => (
                <button
                  key={strategy.id}
                  onClick={() => setSelectedStrategy(strategy)}
                  className={`w-full text-left px-4 py-3 hover:bg-gray-800 transition-colors ${
                    selectedStrategy?.id === strategy.id ? 'bg-gray-800' : ''
                  }`}
                >
                  <h4 className="text-sm font-medium text-gray-200 mb-1">{strategy.name}</h4>
                  <p className="text-xs text-gray-500 mb-2 line-clamp-2">
                    {strategy.description}
                  </p>
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-0.5 text-xs rounded ${getDifficultyColor(strategy.difficulty)}`}>
                      {strategy.difficulty}
                    </span>
                    <span className={`px-2 py-0.5 text-xs rounded ${getCategoryColor(strategy.category)}`}>
                      {strategy.category.replace('-', ' ')}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Strategy Detail */}
      <div className="flex-1 flex flex-col">
        {selectedStrategy ? (
          <>
            {/* Detail Header */}
            <div className="bg-gray-800 border-b border-gray-700 px-6 py-4">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-gray-200">{selectedStrategy.name}</h3>
                  <p className="text-sm text-gray-400 mt-1">{selectedStrategy.description}</p>
                  <div className="flex items-center gap-2 mt-3">
                    <span className={`px-2 py-1 text-xs rounded ${getDifficultyColor(selectedStrategy.difficulty)}`}>
                      {selectedStrategy.difficulty}
                    </span>
                    <span className={`px-2 py-1 text-xs rounded ${getCategoryColor(selectedStrategy.category)}`}>
                      {selectedStrategy.category.replace('-', ' ')}
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => loadStrategy(selectedStrategy)}
                  className="px-4 py-2 bg-canopy-600 hover:bg-canopy-700 text-white text-sm rounded transition-colors flex items-center gap-2"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                    />
                  </svg>
                  Load Strategy
                </button>
              </div>
            </div>

            {/* Detail Content */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {/* Code Preview */}
              <div>
                <h4 className="text-sm font-semibold text-gray-300 mb-2">Strategy Code</h4>
                <div className="bg-gray-800 border border-gray-700 rounded p-4 overflow-x-auto">
                  <pre className="text-sm text-gray-300 font-mono">{selectedStrategy.code}</pre>
                </div>
              </div>

              {/* Expected Performance (if available) */}
              {selectedStrategy.expectedMetrics && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-300 mb-2">
                    Expected Performance
                  </h4>
                  <div className="bg-gray-800 border border-gray-700 rounded p-4">
                    <div className="grid grid-cols-2 gap-4">
                      {Object.entries(selectedStrategy.expectedMetrics).map(([key, value]) => (
                        <div key={key}>
                          <span className="text-xs text-gray-500 block mb-1">
                            {key.replace(/([A-Z])/g, ' $1').trim()}
                          </span>
                          <span className="text-sm text-gray-200 font-medium">{value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Info Box */}
              <div className="p-4 bg-blue-900/20 border border-blue-700 rounded">
                <p className="text-xs text-blue-400">
                  Click "Load Strategy" to copy this code to the editor and start backtesting.
                  You can modify the code to experiment with different parameters.
                </p>
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
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              <h3 className="text-lg font-medium text-gray-400 mb-2">Select a Strategy</h3>
              <p className="text-sm text-gray-500">Choose an example to view details</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
