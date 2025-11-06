"""
Genetic Algorithm Optimizer Adapter.

Implements genetic algorithm optimization using DEAP library.
Uses evolutionary principles: selection, crossover, mutation.
"""

import time
import random
from typing import List, Dict, Any, Callable, Optional
import numpy as np
from deap import base, creator, tools, algorithms
from canopy.ports.optimizer import IOptimizer
from canopy.domain.optimization import (
    ParameterSpace,
    ObjectiveFunction,
    OptimizationResult,
)


class GeneticAlgorithmOptimizer(IOptimizer):
    """
    Genetic Algorithm optimizer adapter.

    Uses evolutionary principles to search parameter space:
    - Selection: Choose best individuals
    - Crossover: Combine parent genes
    - Mutation: Random changes for diversity
    - Elitism: Preserve best solutions
    """

    def __init__(
        self,
        population_size: int = 50,
        n_generations: int = 100,
        crossover_prob: float = 0.8,
        mutation_prob: float = 0.2,
        early_stopping_rounds: Optional[int] = None,
        random_seed: Optional[int] = None
    ):
        """
        Initialize genetic algorithm optimizer.

        Args:
            population_size: Number of individuals in population
            n_generations: Maximum number of generations
            crossover_prob: Probability of crossover (0-1)
            mutation_prob: Probability of mutation (0-1)
            early_stopping_rounds: Stop if no improvement for N generations
            random_seed: Random seed for reproducibility
        """
        self.population_size = population_size
        self.n_generations = n_generations
        self.crossover_prob = crossover_prob
        self.mutation_prob = mutation_prob
        self.early_stopping_rounds = early_stopping_rounds
        self.random_seed = random_seed

    def optimize(
        self,
        objective_function: Callable[[Dict[str, Any]], float],
        parameter_spaces: List[ParameterSpace],
        objective: ObjectiveFunction,
    ) -> OptimizationResult:
        """
        Optimize using genetic algorithm.

        Args:
            objective_function: Function to optimize
            parameter_spaces: List of parameter spaces
            objective: Objective configuration

        Returns:
            OptimizationResult with optimal parameters
        """
        if self.random_seed is not None:
            random.seed(self.random_seed)
            np.random.seed(self.random_seed)

        start_time = time.time()

        # Setup DEAP
        # Clear any existing fitness/individual classes
        if hasattr(creator, "FitnessMax"):
            del creator.FitnessMax
        if hasattr(creator, "Individual"):
            del creator.Individual

        # Create fitness class (maximize or minimize)
        if objective.maximize:
            creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        else:
            creator.create("FitnessMax", base.Fitness, weights=(-1.0,))

        creator.create("Individual", list, fitness=creator.FitnessMax)

        toolbox = base.Toolbox()

        # Register parameter generators
        for i, ps in enumerate(parameter_spaces):
            if ps.type == "integer":
                toolbox.register(
                    f"attr_{i}",
                    random.randint,
                    int(ps.min_value),
                    int(ps.max_value)
                )
            else:
                toolbox.register(
                    f"attr_{i}",
                    random.uniform,
                    ps.min_value,
                    ps.max_value
                )

        # Register individual and population
        toolbox.register(
            "individual",
            tools.initCycle,
            creator.Individual,
            [getattr(toolbox, f"attr_{i}") for i in range(len(parameter_spaces))],
            n=1
        )
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)

        # Register evaluation function
        def evaluate(individual):
            params = {
                ps.name: individual[i]
                for i, ps in enumerate(parameter_spaces)
            }
            try:
                value = objective_function(params)
                return (value,)
            except Exception:
                # Return worst possible fitness for failed evaluations
                return (float('-inf') if objective.maximize else float('inf'),)

        toolbox.register("evaluate", evaluate)

        # Register genetic operators
        # Use blend crossover for single parameter, two-point for multiple
        if len(parameter_spaces) == 1:
            toolbox.register("mate", tools.cxBlend, alpha=0.5)
        else:
            toolbox.register("mate", tools.cxTwoPoint)
        toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.2)
        toolbox.register("select", tools.selTournament, tournsize=3)

        # Create initial population
        population = toolbox.population(n=self.population_size)

        # Track statistics
        convergence_history = []
        evaluations = 0
        best_fitness = float('-inf') if objective.maximize else float('inf')
        generations_without_improvement = 0

        # Evaluate initial population
        fitnesses = map(toolbox.evaluate, population)
        for ind, fit in zip(population, fitnesses):
            ind.fitness.values = fit
            evaluations += 1

        # Evolution loop
        for generation in range(self.n_generations):
            # Select next generation
            offspring = toolbox.select(population, len(population))
            offspring = list(map(toolbox.clone, offspring))

            # Apply crossover
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < self.crossover_prob:
                    toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values

            # Apply mutation
            for mutant in offspring:
                if random.random() < self.mutation_prob:
                    toolbox.mutate(mutant)
                    del mutant.fitness.values

            # Evaluate offspring with invalid fitness
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit
                evaluations += 1

            # Replace population (elitism: keep best)
            population[:] = offspring

            # Track best fitness
            current_best = tools.selBest(population, 1)[0]
            current_fitness = current_best.fitness.values[0]

            # Check for improvement
            if objective.maximize:
                improved = current_fitness > best_fitness
            else:
                improved = abs(current_fitness) < abs(best_fitness)

            if improved:
                best_fitness = current_fitness
                generations_without_improvement = 0
            else:
                generations_without_improvement += 1

            convergence_history.append(best_fitness)

            # Early stopping
            if (self.early_stopping_rounds is not None and
                generations_without_improvement >= self.early_stopping_rounds):
                break

        # Extract best solution
        best_individual = tools.selBest(population, 1)[0]
        best_params = {
            ps.name: best_individual[i]
            for i, ps in enumerate(parameter_spaces)
        }

        # Round integer parameters
        for ps in parameter_spaces:
            if ps.type == "integer":
                best_params[ps.name] = int(round(best_params[ps.name]))

        best_value = best_individual.fitness.values[0]

        optimization_time = time.time() - start_time

        return OptimizationResult(
            parameters=best_params,
            objective_value=best_value,
            metrics={objective.metric_name: best_value},
            backtest_count=evaluations,
            optimization_time=optimization_time,
            maximize=objective.maximize,
            convergence_history=convergence_history
        )

    def supports_parallel(self) -> bool:
        """GA can support parallel evaluation (not implemented yet)"""
        return True

    def supports_early_stopping(self) -> bool:
        """GA supports early stopping"""
        return True
