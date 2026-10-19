from __future__ import annotations

import random
from pathlib import Path

from algorithms import ALGORITHMS
from algorithms.base import SearchResult
from algorithms.genetic import GeneticAlgorithm
from core.io_utils import save_result
from core.models import Package, Truck
from core.objective import is_valid
from core.state import State

N_RUNS = 3

GA_CONTROL_POPULATION = 50
GA_ITERATION_VARIANTS = (50, 100, 200)
GA_CONTROL_ITERATIONS = 100
GA_POPULATION_VARIANTS = (20, 50, 100)

def _seed_for(seed: int | None, i: int) -> int | None:
    return None if seed is None else seed + i

def run_repeated(algo_key: str, truck: Truck, packages: dict[str, Package],
                 n_runs: int = N_RUNS, seed: int | None = None,
                 **params) -> list[tuple[SearchResult, Path]]:
    results = []
    for i in range(n_runs):
        run_seed = _seed_for(seed, i)
        initial = State.random_initial(truck, packages, random.Random(run_seed))
        algo = ALGORITHMS[algo_key](seed=run_seed, **params)
        result = algo.run(initial)
        path = save_result(result.to_dict(), f"{algo.name}_run{i + 1}")
        results.append((result, path))
    return results

def run_ga_experiment(truck: Truck, packages: dict[str, Package],
                      n_runs: int = N_RUNS,
                      seed: int | None = None) -> list[tuple[SearchResult, Path]]:
    configs = [(GA_CONTROL_POPULATION, it) for it in GA_ITERATION_VARIANTS]
    configs += [(pop, GA_CONTROL_ITERATIONS) for pop in GA_POPULATION_VARIANTS]
    configs = list(dict.fromkeys(configs))

    results = []
    for pop, it in configs:
        for i in range(n_runs):
            run_seed = _seed_for(seed, i)
            initial = State.random_initial(truck, packages, random.Random(run_seed))
            algo = GeneticAlgorithm(population_size=pop, max_iterations=it, seed=run_seed)
            result = algo.run(initial)
            path = save_result(result.to_dict(), f"{algo.name}_pop{pop}_iter{it}_run{i + 1}")
            results.append((result, path))
    return results

def summarize(results: list[SearchResult]) -> None:
    for i, r in enumerate(results, 1):
        print(f"[{r.algorithm} #{i}] init={r.initial_objective:.2f} "
              f"final={r.final_objective:.2f} valid={is_valid(r.final_state)} "
              f"iter={r.iterations} time={r.duration_s:.3f}s")
        e = r.extra
        if "iterations_per_restart" in e:
            print(f"    restart={e['restarts']} iterasi per restart={e['iterations_per_restart']}")
        if "stuck_count" in e:
            print(f"    frekuensi stuck di local optima={e['stuck_count']}")
        if "population_size" in e:
            print(f"    populasi={e['population_size']} iterasi={r.iterations}")
        if "accepted_moves" in e:
            print(f"    move diterima={e['accepted_moves']}")
