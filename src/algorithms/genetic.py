"""Genetic Algorithm.

Parameter yang divariasikan: jumlah populasi dan banyak iterasi (generasi).
"""

from __future__ import annotations

from typing import Any

from core.neighbors import apply_move, random_move
from core.objective import objective
from core.state import Placement, State

from .base import LocalSearch


class GeneticAlgorithm(LocalSearch):
    name = "genetic_algorithm"

    def __init__(
        self,
        population_size: int = 50,
        max_iterations: int = 100,
        mutation_rate: float = 0.1,
        elitism: int = 1,
        seed: int | None = None,
    ):
        super().__init__(seed)
        if population_size < 2:
            raise ValueError("population_size minimal 2 agar crossover bisa dilakukan.")
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.mutation_rate = mutation_rate
        self.elitism = min(elitism, population_size)

    def init_population(self, initial: State) -> list[State]:
        """Populasi awal: `initial` + State.random_initial(...) sebanyak population_size - 1."""
        population = [initial]
        for _ in range(self.population_size - 1):
            population.append(State.random_initial(initial.truck, initial.packages, self.rng))
        return population

    def fitness(self, state: State) -> float:
        return objective(state)

    def select(self, population: list[State], fitnesses: list[float]) -> State:
        """Roulette wheel: peluang terpilih sebanding dengan fitness.
        Fitness digeser (f - f_min + 1) agar semua bobot positif."""
        f_min = min(fitnesses)
        weights = [f - f_min + 1 for f in fitnesses]
        return self.rng.choices(population, weights=weights, k=1)[0]

    def crossover(self, a: State, b: State) -> tuple[State, State]:
        """Single-point crossover: gen (placement per paket) setelah titik potong ditukar."""
        ids = list(a.placements)
        if len(ids) < 2:
            return a.copy(), b.copy()

        point = self.rng.randint(1, len(ids) - 1)
        c1, c2 = a.copy(), b.copy()
        for pid in ids[point:]:
            pa, pb = a.placements[pid], b.placements[pid]
            c1.placements[pid] = Placement(pb.position, pb.orientation)
            c2.placements[pid] = Placement(pa.position, pa.orientation)
        return c1, c2

    def mutate(self, state: State) -> State:
        """Dengan peluang mutation_rate, terapkan satu langkah neighbor acak (swap/move/rotate)."""
        if self.rng.random() >= self.mutation_rate:
            return state
        try:
            return apply_move(state, random_move(state, self.rng))
        except ValueError:
            # tidak ada neighbor yang mengubah state
            return state

    def _search(self, initial: State) -> tuple[State, int, list[float], dict[str, Any]]:
        max_history: list[float] = []  # objective maksimum per generasi
        avg_history: list[float] = []  # objective rata-rata per generasi

        population = self.init_population(initial)
        fitnesses = [self.fitness(s) for s in population]

        best_idx = max(range(len(population)), key=fitnesses.__getitem__)
        best, best_val = population[best_idx], fitnesses[best_idx]
        initial_best_val = best_val

        max_history.append(max(fitnesses))
        avg_history.append(sum(fitnesses) / len(fitnesses))

        for _ in range(self.max_iterations):
            # elitism: individu terbaik langsung dibawa ke generasi berikutnya
            ranked = sorted(range(len(population)), key=fitnesses.__getitem__, reverse=True)
            new_pop = [population[i] for i in ranked[:self.elitism]]

            while len(new_pop) < self.population_size:
                p1 = self.select(population, fitnesses)
                p2 = self.select(population, fitnesses)
                c1, c2 = self.crossover(p1, p2)
                new_pop += [self.mutate(c1), self.mutate(c2)]

            population = new_pop[:self.population_size]
            fitnesses = [self.fitness(s) for s in population]

            gen_best = max(range(len(population)), key=fitnesses.__getitem__)
            if fitnesses[gen_best] > best_val:
                best, best_val = population[gen_best], fitnesses[gen_best]

            max_history.append(max(fitnesses))
            avg_history.append(sum(fitnesses) / len(fitnesses))

        return best, self.max_iterations, max_history, {
            "population_size": self.population_size,
            "mutation_rate": self.mutation_rate,
            "elitism": self.elitism,
            "initial_best_objective": initial_best_val,
            "avg_history": avg_history,
        }
