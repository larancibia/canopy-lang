"""
Optimize Strategy Use Case - Application layer for strategy optimization.

This module orchestrates strategy parameter optimization using various
optimization algorithms.
"""

from typing import Dict, Any, List, Type
import hashlib
import json
from canopy.ports.optimizer import IOptimizer
from canopy.ports.backtest_engine import IBacktestEngine
from canopy.adapters.engines.simple_engine import SimpleBacktestEngine
from canopy.domain.strategy import Strategy
from canopy.domain.timeseries import TimeSeries
from canopy.domain.optimization import (
    ParameterSpace,
    ObjectiveFunction,
    OptimizationResult,
)
from canopy.domain.metrics import (
    sharpe_ratio,
    sortino_ratio,
    max_drawdown,
    calmar_ratio,
)


class OptimizeStrategyUseCase:
    """
    Application use case for optimizing strategy parameters.

    This class orchestrates the optimization process by:
    1. Running backtests for different parameter combinations
    2. Calculating objective metrics
    3. Finding optimal parameters
    4. Optionally caching results to avoid redundant computation
    """

    def __init__(
        self,
        optimizer: IOptimizer,
        timeseries: TimeSeries,
        backtest_engine: IBacktestEngine = None,
        initial_capital: float = 10000.0,
        commission: float = 0.0,
        slippage: float = 0.0,
        enable_cache: bool = True
    ):
        """
        Initialize optimization use case.

        Args:
            optimizer: Optimizer adapter to use
            timeseries: Historical data for backtesting
            backtest_engine: Backtest engine (defaults to SimpleBacktestEngine)
            initial_capital: Starting capital for backtests
            commission: Commission per trade
            slippage: Slippage per trade
            enable_cache: Whether to cache backtest results
        """
        self.optimizer = optimizer
        self.timeseries = timeseries
        self.engine = backtest_engine or SimpleBacktestEngine()
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.enable_cache = enable_cache
        self._cache: Dict[str, float] = {}

    def optimize(
        self,
        strategy_class: Type[Strategy],
        parameter_spaces: List[ParameterSpace],
        objective: ObjectiveFunction,
        initial_capital: float = None,
    ) -> OptimizationResult:
        """
        Optimize strategy parameters.

        Args:
            strategy_class: Strategy class to optimize (e.g., MACrossoverStrategy)
            parameter_spaces: List of parameter spaces to search
            objective: Objective function to optimize
            initial_capital: Override default initial capital

        Returns:
            OptimizationResult with optimal parameters
        """
        capital = initial_capital if initial_capital is not None else self.initial_capital

        # Create objective function for optimizer
        def objective_func(params: Dict[str, Any]) -> float:
            """
            Evaluate strategy with given parameters.

            Args:
                params: Dictionary of parameter values

            Returns:
                Objective metric value
            """
            # Check cache
            cache_key = self._get_cache_key(strategy_class.__name__, params)
            if self.enable_cache and cache_key in self._cache:
                return self._cache[cache_key]

            # Create strategy instance with parameters
            strategy = strategy_class(name=strategy_class.__name__, **params)

            # Run backtest
            try:
                backtest = self.engine.run(
                    strategy=strategy,
                    timeseries=self.timeseries,
                    initial_capital=capital,
                    commission=self.commission,
                    slippage=self.slippage
                )

                # Calculate returns for metrics
                returns = backtest.equity_curve.pct_change().dropna()

                # Get objective metric value
                if objective.metric_name == "sharpe_ratio":
                    value = sharpe_ratio(returns)
                elif objective.metric_name == "sortino_ratio":
                    value = sortino_ratio(returns)
                elif objective.metric_name == "max_drawdown":
                    value = max_drawdown(backtest.equity_curve)
                elif objective.metric_name == "calmar_ratio":
                    value = calmar_ratio(returns)
                elif objective.metric_name == "total_return":
                    value = backtest.total_return()
                else:
                    # Default to Sharpe ratio
                    value = sharpe_ratio(returns)

                # Cache result
                if self.enable_cache:
                    self._cache[cache_key] = value

                return value

            except Exception as e:
                # Return worst possible value for failed backtests
                return float('-inf') if objective.maximize else float('inf')

        # Run optimization
        result = self.optimizer.optimize(
            objective_function=objective_func,
            parameter_spaces=parameter_spaces,
            objective=objective
        )

        return result

    def _get_cache_key(self, strategy_name: str, params: Dict[str, Any]) -> str:
        """
        Generate cache key for parameter combination.

        Args:
            strategy_name: Name of strategy
            params: Parameter dictionary

        Returns:
            Cache key string
        """
        # Create deterministic key from strategy name and params
        params_str = json.dumps(params, sort_keys=True)
        key_str = f"{strategy_name}:{params_str}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def clear_cache(self):
        """Clear the backtest results cache"""
        self._cache.clear()

    def get_cache_size(self) -> int:
        """
        Get number of cached results.

        Returns:
            Number of cached backtest results
        """
        return len(self._cache)
