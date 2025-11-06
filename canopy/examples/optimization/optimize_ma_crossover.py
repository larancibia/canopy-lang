"""
Strategy Optimization Example

This example demonstrates how to optimize strategy parameters
using various methods including grid search and genetic algorithms.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from itertools import product
import matplotlib.pyplot as plt


def backtest_ma_crossover(
    prices: pd.Series, fast_period: int, slow_period: int, commission: float = 0.001
) -> Dict:
    """
    Backtest moving average crossover strategy.

    Args:
        prices: Price series
        fast_period: Fast MA period
        slow_period: Slow MA period
        commission: Commission rate

    Returns:
        Dictionary with performance metrics
    """
    if fast_period >= slow_period:
        return {"sharpe_ratio": -999, "total_return": -1, "max_drawdown": -1}

    # Calculate moving averages
    fast_ma = prices.rolling(window=fast_period).mean()
    slow_ma = prices.rolling(window=slow_period).mean()

    # Generate signals
    signals = pd.DataFrame(index=prices.index)
    signals["price"] = prices
    signals["fast_ma"] = fast_ma
    signals["slow_ma"] = slow_ma
    signals["signal"] = 0

    # Buy when fast crosses above slow, sell when crosses below
    signals["signal"][fast_period:] = np.where(
        signals["fast_ma"][fast_period:] > signals["slow_ma"][fast_period:], 1, 0
    )

    signals["positions"] = signals["signal"].diff()

    # Calculate returns
    initial_capital = 10000
    positions = pd.DataFrame(index=signals.index).fillna(0.0)
    positions["stock"] = 100 * signals["signal"]

    portfolio = positions.multiply(signals["price"], axis=0)
    pos_diff = positions.diff()

    portfolio["holdings"] = positions.multiply(signals["price"], axis=0).sum(axis=1)
    portfolio["cash"] = (
        initial_capital
        - (pos_diff.multiply(signals["price"], axis=0).sum(axis=1)).cumsum()
    )

    # Apply commission
    portfolio["cash"] -= abs(pos_diff["stock"]) * signals["price"] * commission

    portfolio["total"] = portfolio["cash"] + portfolio["holdings"]
    portfolio["returns"] = portfolio["total"].pct_change()

    # Calculate metrics
    total_return = (portfolio["total"].iloc[-1] - initial_capital) / initial_capital

    returns = portfolio["returns"].dropna()
    sharpe_ratio = (
        (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0
    )

    # Max drawdown
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.cummax()
    drawdown = (cumulative - running_max) / running_max
    max_drawdown = drawdown.min()

    # Win rate
    winning_trades = (pos_diff["stock"] * returns).dropna()
    win_rate = (winning_trades > 0).sum() / len(winning_trades) if len(winning_trades) > 0 else 0

    return {
        "sharpe_ratio": sharpe_ratio,
        "total_return": total_return,
        "max_drawdown": max_drawdown,
        "win_rate": win_rate,
        "total_trades": abs(pos_diff["stock"]).sum() / 100 / 2,
    }


def grid_search_optimization(
    prices: pd.Series,
    fast_range: List[int],
    slow_range: List[int],
    objective: str = "sharpe_ratio",
) -> Tuple[Dict, pd.DataFrame]:
    """
    Perform grid search optimization.

    Args:
        prices: Price series
        fast_range: Range of fast MA periods to test
        slow_range: Range of slow MA periods to test
        objective: Objective to optimize ('sharpe_ratio', 'total_return', etc.)

    Returns:
        Tuple of (best parameters, results DataFrame)
    """
    print("Starting grid search optimization...")
    print(f"Fast MA range: {fast_range}")
    print(f"Slow MA range: {slow_range}")
    print(f"Total combinations: {len(fast_range) * len(slow_range)}")

    results = []

    for fast, slow in product(fast_range, slow_range):
        if fast >= slow:
            continue

        metrics = backtest_ma_crossover(prices, fast, slow)
        results.append(
            {
                "fast_period": fast,
                "slow_period": slow,
                **metrics,
            }
        )

    results_df = pd.DataFrame(results)

    # Find best parameters
    best_idx = results_df[objective].idxmax()
    best_params = results_df.loc[best_idx].to_dict()

    print(f"\nBest parameters (by {objective}):")
    print(f"  Fast MA: {int(best_params['fast_period'])}")
    print(f"  Slow MA: {int(best_params['slow_period'])}")
    print(f"  {objective}: {best_params[objective]:.4f}")

    return best_params, results_df


def walk_forward_optimization(
    prices: pd.Series,
    fast_range: List[int],
    slow_range: List[int],
    in_sample_ratio: float = 0.7,
    num_windows: int = 5,
) -> List[Dict]:
    """
    Perform walk-forward optimization.

    Args:
        prices: Price series
        fast_range: Range of fast MA periods
        slow_range: Range of slow MA periods
        in_sample_ratio: Ratio of in-sample data
        num_windows: Number of walk-forward windows

    Returns:
        List of results for each window
    """
    print("\nStarting walk-forward optimization...")
    print(f"Number of windows: {num_windows}")
    print(f"In-sample ratio: {in_sample_ratio}")

    results = []
    window_size = len(prices) // num_windows

    for i in range(num_windows):
        print(f"\n--- Window {i+1}/{num_windows} ---")

        # Define in-sample and out-of-sample periods
        start_idx = i * window_size
        split_idx = int(start_idx + window_size * in_sample_ratio)
        end_idx = min(start_idx + window_size, len(prices))

        in_sample = prices.iloc[start_idx:split_idx]
        out_of_sample = prices.iloc[split_idx:end_idx]

        # Optimize on in-sample data
        best_params, _ = grid_search_optimization(
            in_sample, fast_range, slow_range, objective="sharpe_ratio"
        )

        # Test on out-of-sample data
        oos_metrics = backtest_ma_crossover(
            out_of_sample,
            int(best_params["fast_period"]),
            int(best_params["slow_period"]),
        )

        results.append(
            {
                "window": i + 1,
                "fast_period": int(best_params["fast_period"]),
                "slow_period": int(best_params["slow_period"]),
                "in_sample_sharpe": best_params["sharpe_ratio"],
                "out_of_sample_sharpe": oos_metrics["sharpe_ratio"],
                "out_of_sample_return": oos_metrics["total_return"],
            }
        )

    results_df = pd.DataFrame(results)

    print("\n=== Walk-Forward Results ===")
    print(results_df)

    print(f"\nAverage out-of-sample Sharpe: {results_df['out_of_sample_sharpe'].mean():.4f}")
    print(f"Average out-of-sample Return: {results_df['out_of_sample_return'].mean():.4f}")

    return results


def genetic_algorithm_optimization(
    prices: pd.Series,
    fast_range: Tuple[int, int],
    slow_range: Tuple[int, int],
    population_size: int = 50,
    generations: int = 20,
    mutation_rate: float = 0.1,
) -> Dict:
    """
    Optimize using genetic algorithm.

    Args:
        prices: Price series
        fast_range: (min, max) for fast MA period
        slow_range: (min, max) for slow MA period
        population_size: Number of individuals in population
        generations: Number of generations
        mutation_rate: Probability of mutation

    Returns:
        Best parameters found
    """
    print("\nStarting genetic algorithm optimization...")
    print(f"Population size: {population_size}")
    print(f"Generations: {generations}")

    def create_individual():
        """Create random parameter set."""
        fast = np.random.randint(fast_range[0], fast_range[1])
        slow = np.random.randint(max(fast + 1, slow_range[0]), slow_range[1])
        return {"fast": fast, "slow": slow}

    def fitness(individual):
        """Calculate fitness (Sharpe ratio)."""
        metrics = backtest_ma_crossover(prices, individual["fast"], individual["slow"])
        return metrics["sharpe_ratio"]

    def crossover(parent1, parent2):
        """Combine two parents."""
        return {
            "fast": parent1["fast"] if np.random.random() > 0.5 else parent2["fast"],
            "slow": parent1["slow"] if np.random.random() > 0.5 else parent2["slow"],
        }

    def mutate(individual):
        """Randomly mutate individual."""
        if np.random.random() < mutation_rate:
            individual["fast"] = np.random.randint(fast_range[0], fast_range[1])
        if np.random.random() < mutation_rate:
            individual["slow"] = np.random.randint(
                max(individual["fast"] + 1, slow_range[0]), slow_range[1]
            )
        return individual

    # Initialize population
    population = [create_individual() for _ in range(population_size)]

    best_individual = None
    best_fitness = -np.inf

    for gen in range(generations):
        # Evaluate fitness
        fitness_scores = [(ind, fitness(ind)) for ind in population]
        fitness_scores.sort(key=lambda x: x[1], reverse=True)

        # Track best
        if fitness_scores[0][1] > best_fitness:
            best_fitness = fitness_scores[0][1]
            best_individual = fitness_scores[0][0]

        if (gen + 1) % 5 == 0:
            print(
                f"Generation {gen+1}: Best Sharpe = {best_fitness:.4f}, "
                f"Params = Fast:{best_individual['fast']}, Slow:{best_individual['slow']}"
            )

        # Selection (top 50%)
        selected = [ind for ind, _ in fitness_scores[: population_size // 2]]

        # Create new generation
        new_population = selected.copy()

        while len(new_population) < population_size:
            # Tournament selection
            parent1 = selected[np.random.randint(len(selected))]
            parent2 = selected[np.random.randint(len(selected))]

            # Crossover
            child = crossover(parent1, parent2)

            # Mutation
            child = mutate(child)

            new_population.append(child)

        population = new_population

    print(f"\nBest parameters found:")
    print(f"  Fast MA: {best_individual['fast']}")
    print(f"  Slow MA: {best_individual['slow']}")
    print(f"  Sharpe Ratio: {best_fitness:.4f}")

    return best_individual


def visualize_optimization_results(results_df: pd.DataFrame):
    """
    Visualize optimization results.

    Args:
        results_df: DataFrame with optimization results
    """
    print("\nGenerating visualization...")

    # Create heatmap of Sharpe ratios
    pivot = results_df.pivot(
        index="slow_period", columns="fast_period", values="sharpe_ratio"
    )

    plt.figure(figsize=(12, 8))
    plt.imshow(pivot, cmap="RdYlGn", aspect="auto")
    plt.colorbar(label="Sharpe Ratio")
    plt.xlabel("Fast MA Period")
    plt.ylabel("Slow MA Period")
    plt.title("MA Crossover Optimization - Sharpe Ratio Heatmap")

    # Add annotations for best performers
    best_idx = results_df["sharpe_ratio"].idxmax()
    best_fast = results_df.loc[best_idx, "fast_period"]
    best_slow = results_df.loc[best_idx, "slow_period"]

    plt.scatter([best_fast], [best_slow], color="red", s=200, marker="*", zorder=10)
    plt.text(
        best_fast, best_slow, "  Best", color="red", fontsize=12, fontweight="bold"
    )

    plt.tight_layout()
    plt.savefig("optimization_heatmap.png")
    print("Saved visualization to optimization_heatmap.png")


def example_optimization():
    """
    Complete optimization example.
    """
    from canopy.adapters.data.yahoo_provider import YahooProvider

    print("=== Strategy Optimization Example ===\n")

    # Fetch data
    print("Fetching data...")
    provider = YahooProvider()
    data = provider.fetch_data("AAPL", "2020-01-01", "2023-12-31")

    prices = pd.Series([bar.close for bar in data.bars])
    print(f"Data points: {len(prices)}")

    # 1. Grid Search
    print("\n" + "=" * 50)
    print("Method 1: Grid Search")
    print("=" * 50)

    fast_range = list(range(5, 50, 5))
    slow_range = list(range(50, 200, 10))

    best_params, results_df = grid_search_optimization(
        prices, fast_range, slow_range, objective="sharpe_ratio"
    )

    # Visualize
    visualize_optimization_results(results_df)

    # 2. Walk-Forward Optimization
    print("\n" + "=" * 50)
    print("Method 2: Walk-Forward Optimization")
    print("=" * 50)

    wfo_results = walk_forward_optimization(
        prices, fast_range=list(range(5, 30, 5)), slow_range=list(range(30, 100, 10))
    )

    # 3. Genetic Algorithm
    print("\n" + "=" * 50)
    print("Method 3: Genetic Algorithm")
    print("=" * 50)

    ga_best = genetic_algorithm_optimization(
        prices,
        fast_range=(5, 50),
        slow_range=(50, 200),
        population_size=30,
        generations=15,
    )

    print("\n=== Optimization Complete ===")


if __name__ == "__main__":
    example_optimization()
