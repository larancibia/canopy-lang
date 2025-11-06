import { useState } from 'react';
import { EditorPanel } from '../components/EditorPanel';
import { BacktestPanel } from '../components/BacktestPanel';
import { ResultsPanel } from '../components/ResultsPanel';
import { IndicatorLibrary } from '../components/IndicatorLibrary';
import { StrategyExplorer } from '../components/StrategyExplorer';

type ViewMode = 'split' | 'editor-only' | 'results-only';
type SidePanel = 'none' | 'indicators' | 'examples';

export const Editor = () => {
  const [viewMode, setViewMode] = useState<ViewMode>('split');
  const [sidePanel, setSidePanel] = useState<SidePanel>('none');

  const toggleSidePanel = (panel: SidePanel) => {
    setSidePanel(sidePanel === panel ? 'none' : panel);
  };

  return (
    <div className="h-screen flex flex-col bg-gray-900">
      {/* Toolbar */}
      <div className="bg-gray-800 border-b border-gray-700 px-4 py-2 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <button
            onClick={() => toggleSidePanel('examples')}
            className={`px-3 py-1.5 text-sm rounded transition-colors ${
              sidePanel === 'examples'
                ? 'bg-canopy-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            Examples
          </button>
          <button
            onClick={() => toggleSidePanel('indicators')}
            className={`px-3 py-1.5 text-sm rounded transition-colors ${
              sidePanel === 'indicators'
                ? 'bg-canopy-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            Indicators
          </button>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500 mr-2">View:</span>
          <button
            onClick={() => setViewMode('editor-only')}
            className={`px-3 py-1.5 text-sm rounded transition-colors ${
              viewMode === 'editor-only'
                ? 'bg-gray-700 text-white'
                : 'bg-gray-900 text-gray-400 hover:bg-gray-700'
            }`}
          >
            Editor
          </button>
          <button
            onClick={() => setViewMode('split')}
            className={`px-3 py-1.5 text-sm rounded transition-colors ${
              viewMode === 'split'
                ? 'bg-gray-700 text-white'
                : 'bg-gray-900 text-gray-400 hover:bg-gray-700'
            }`}
          >
            Split
          </button>
          <button
            onClick={() => setViewMode('results-only')}
            className={`px-3 py-1.5 text-sm rounded transition-colors ${
              viewMode === 'results-only'
                ? 'bg-gray-700 text-white'
                : 'bg-gray-900 text-gray-400 hover:bg-gray-700'
            }`}
          >
            Results
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Side Panel */}
        {sidePanel !== 'none' && (
          <div className="w-[600px] border-r border-gray-700">
            {sidePanel === 'indicators' && <IndicatorLibrary />}
            {sidePanel === 'examples' && <StrategyExplorer />}
          </div>
        )}

        {/* Main Workspace */}
        <div className="flex-1 flex overflow-hidden">
          {/* Editor Section */}
          {(viewMode === 'editor-only' || viewMode === 'split') && (
            <div
              className={`${
                viewMode === 'split' ? 'w-1/2 border-r border-gray-700' : 'flex-1'
              } flex flex-col`}
            >
              <div className="flex-1 overflow-hidden">
                <EditorPanel />
              </div>
            </div>
          )}

          {/* Right Panel (Backtest Config + Results) */}
          {(viewMode === 'results-only' || viewMode === 'split') && (
            <div className={`${viewMode === 'split' ? 'w-1/2' : 'flex-1'} flex flex-col`}>
              {/* Backtest Configuration - collapsible */}
              <div className="w-80 border-r border-gray-700">
                <BacktestPanel />
              </div>

              {/* Results Panel */}
              <div className="flex-1 overflow-hidden">
                <ResultsPanel />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
