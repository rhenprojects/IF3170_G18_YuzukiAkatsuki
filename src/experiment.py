from __future__ import annotations

from algorithms import ALGORITHMS
from algorithms.base import SearchResult
from core.io_utils import save_result
from core.models import Package, Truck
from core.state import State

N_RUNS = 3

def run_repeated(algo_key: str, truck: Truck, packages: dict[str, Package],
                 n_runs: int = N_RUNS, **params) -> list[SearchResult]:
    results = []
    for i in range(n_runs):
        initial = State.random_initial(truck, packages)
        algo = ALGORITHMS[algo_key](**params)
        result = algo.run(initial)
        save_result(result.to_dict(), f"{algo.name}_run{i + 1}")
        results.append(result)
    return results

def summarize(results: list[SearchResult]) -> None:
    for i, r in enumerate(results, 1):
        print(f"[{r.algorithm} #{i}] init={r.initial_objective:.2f} "
              f"final={r.final_objective:.2f} iter={r.iterations} "
              f"time={r.duration_s:.3f}s extra_keys={list(r.extra)}")
