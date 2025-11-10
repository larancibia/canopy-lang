// Global state management for Canopy IDE using Zustand

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type {
  Strategy,
  BacktestResult,
  BacktestConfig,
  UIPreferences,
} from '../types/canopy.types';

interface CanopyState {
  // Editor state
  currentStrategy: Strategy | null;
  editorContent: string;
  unsavedChanges: boolean;

  // Backtest state
  backtestConfig: BacktestConfig;
  currentBacktest: BacktestResult | null;
  backtestHistory: BacktestResult[];
  isBacktesting: boolean;

  // UI state
  preferences: UIPreferences;
  sidebarOpen: boolean;
  selectedTab: 'editor' | 'backtest' | 'results';

  // Actions
  setCurrentStrategy: (strategy: Strategy | null) => void;
  setEditorContent: (content: string) => void;
  setUnsavedChanges: (hasChanges: boolean) => void;

  setBacktestConfig: (config: Partial<BacktestConfig>) => void;
  setCurrentBacktest: (result: BacktestResult | null) => void;
  addBacktestToHistory: (result: BacktestResult) => void;
  setIsBacktesting: (isBacktesting: boolean) => void;

  setPreferences: (preferences: Partial<UIPreferences>) => void;
  toggleSidebar: () => void;
  setSelectedTab: (tab: 'editor' | 'backtest' | 'results') => void;

  saveStrategy: () => void;
  loadStrategy: (strategy: Strategy) => void;
  newStrategy: () => void;

  clearBacktestHistory: () => void;
}

const defaultBacktestConfig: BacktestConfig = {
  symbol: 'AAPL',
  startDate: '2023-01-01',
  endDate: '2024-01-01',
  initialCapital: 100000,
  commission: 0.001,
  slippage: 0.0005,
};

const defaultPreferences: UIPreferences = {
  theme: 'dark',
  editorTheme: 'vs-dark',
  fontSize: 14,
  showMinimap: true,
  showLineNumbers: true,
  wordWrap: true,
};

const defaultStrategy = `strategy "My Strategy"

// Define indicators
fast_ma = sma(close, 10)
slow_ma = sma(close, 30)

// Entry condition
buy when crossover(fast_ma, slow_ma)

// Exit condition
sell when crossunder(fast_ma, slow_ma)

// Plot indicators
plot fast_ma
plot slow_ma
`;

export const useCanopyStore = create<CanopyState>()(
  persist(
    (set, get) => ({
      // Initial state
      currentStrategy: null,
      editorContent: defaultStrategy,
      unsavedChanges: false,

      backtestConfig: defaultBacktestConfig,
      currentBacktest: null,
      backtestHistory: [],
      isBacktesting: false,

      preferences: defaultPreferences,
      sidebarOpen: true,
      selectedTab: 'editor',

      // Actions
      setCurrentStrategy: (strategy) => set({ currentStrategy: strategy }),

      setEditorContent: (content) => set({
        editorContent: content,
        unsavedChanges: true,
      }),

      setUnsavedChanges: (hasChanges) => set({ unsavedChanges: hasChanges }),

      setBacktestConfig: (config) => set((state) => ({
        backtestConfig: { ...state.backtestConfig, ...config },
      })),

      setCurrentBacktest: (result) => set({ currentBacktest: result }),

      addBacktestToHistory: (result) => set((state) => ({
        backtestHistory: [result, ...state.backtestHistory].slice(0, 10), // Keep last 10
      })),

      setIsBacktesting: (isBacktesting) => set({ isBacktesting }),

      setPreferences: (preferences) => set((state) => ({
        preferences: { ...state.preferences, ...preferences },
      })),

      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),

      setSelectedTab: (tab) => set({ selectedTab: tab }),

      saveStrategy: () => {
        const state = get();
        if (state.currentStrategy) {
          const updatedStrategy: Strategy = {
            ...state.currentStrategy,
            code: state.editorContent,
            updatedAt: new Date().toISOString(),
          };
          set({
            currentStrategy: updatedStrategy,
            unsavedChanges: false,
          });
        } else {
          // Create new strategy
          const newStrat: Strategy = {
            id: `strategy-${Date.now()}`,
            name: 'Untitled Strategy',
            description: 'A new trading strategy',
            code: state.editorContent,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          };
          set({
            currentStrategy: newStrat,
            unsavedChanges: false,
          });
        }
      },

      loadStrategy: (strategy) => {
        set({
          currentStrategy: strategy,
          editorContent: strategy.code,
          unsavedChanges: false,
        });
      },

      newStrategy: () => {
        set({
          currentStrategy: null,
          editorContent: defaultStrategy,
          unsavedChanges: false,
        });
      },

      clearBacktestHistory: () => set({ backtestHistory: [] }),
    }),
    {
      name: 'canopy-storage',
      partialize: (state) => ({
        preferences: state.preferences,
        backtestConfig: state.backtestConfig,
        backtestHistory: state.backtestHistory,
      }),
    }
  )
);
