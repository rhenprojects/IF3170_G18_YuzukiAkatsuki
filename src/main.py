from __future__ import annotations

import argparse

from algorithms import ALGORITHMS
from core.io_utils import load_problem
from experiment import run_repeated, summarize
from visualization.plots import plot_history


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Local search untuk container loading (Mejiro Express)")
    p.add_argument("--input", required=True, help="Path file JSON problem")
    p.add_argument("--algo", choices=ALGORITHMS.keys(), required=True)
    p.add_argument("--runs", type=int, default=1)
    p.add_argument("--no-plot", action="store_true")
    p.add_argument("--ga-experiment", action="store_true",
                   help="Jalankan seluruh skenario eksperimen GA")
    # parameter algoritma
    p.add_argument("--max-sideways", type=int)
    p.add_argument("--max-restart", type=int)
    p.add_argument("--max-iterations", type=int)
    p.add_argument("--population", type=int)
    return p.parse_args()

def algo_params(args: argparse.Namespace) -> dict:
    mapping = {
        "sideways": {"max_sideways": args.max_sideways},
        "random_restart": {"max_restart": args.max_restart},
        "stochastic": {"max_iterations": args.max_iterations},
        "sa": {"max_iterations": args.max_iterations},
        "ga": {"population_size": args.population, "max_iterations": args.max_iterations},
    }
    return {k: v for k, v in mapping.get(args.algo, {}).items() if v is not None}

def main() -> None:
    args = parse_args()
    truck, packages = load_problem(args.input)

    results = run_repeated(args.algo, truck, packages, n_runs=args.runs, **algo_params(args))
    summarize(results)

    if args.no_plot:
        return
    for r in results:
        extra = {"rata-rata populasi": r.extra["avg_history"]} if "avg_history" in r.extra else None
        plot_history(r.history, f"{r.algorithm}: objective vs iterasi", extra)


if __name__ == "__main__":
    main()
