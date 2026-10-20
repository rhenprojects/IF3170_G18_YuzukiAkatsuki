from __future__ import annotations

import argparse
from pathlib import Path

from algorithms import ALGORITHMS
from algorithms.base import SearchResult
from core.io_utils import load_problem
from core.objective import OBJECTIVE_MODES, set_objective_mode
from experiment import run_ga_experiment, run_repeated, summarize
from visualization.plots import plot_acceptance_probability, plot_history, plot_state


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Local search untuk container loading (Mejiro Express)")
    p.add_argument("--input", required=True, help="Path file JSON problem")
    p.add_argument("--algo", choices=ALGORITHMS.keys())
    p.add_argument("--runs", type=int, default=3, help="Banyak run (spesifikasi: 3 kali)")
    p.add_argument("--seed", type=int, help="Seed agar hasil dapat direproduksi (run ke-i memakai seed+i)")
    p.add_argument("--no-plot", action="store_true", help="Jangan buat plot sama sekali")
    p.add_argument("--show", action="store_true",
                   help="Tampilkan plot secara interaktif (plot selalu disimpan ke folder output)")
    p.add_argument("--ga-experiment", action="store_true",
                   help="Jalankan seluruh skenario eksperimen GA")
    p.add_argument("--objective", choices=OBJECTIVE_MODES, default="value",
                   help="Fungsi objektif: value = total value (default), "
                        "density = total value/berat tiap paket")
    # parameter algoritma
    p.add_argument("--max-sideways", type=int)
    p.add_argument("--max-restart", type=int)
    p.add_argument("--max-iterations", type=int)
    p.add_argument("--population", type=int)
    args = p.parse_args()
    if not args.algo and not args.ga_experiment:
        p.error("pilih --algo atau --ga-experiment")
    return args

def algo_params(args: argparse.Namespace) -> dict:
    mapping = {
        "sideways": {"max_sideways": args.max_sideways},
        "random_restart": {"max_restart": args.max_restart},
        "stochastic": {"max_iterations": args.max_iterations},
        "sa": {"max_iterations": args.max_iterations},
        "ga": {"population_size": args.population, "max_iterations": args.max_iterations},
    }
    return {k: v for k, v in mapping.get(args.algo, {}).items() if v is not None}

def plot_result(r: SearchResult, json_path: Path, show: bool) -> None:
    """Simpan (dan opsional tampilkan) visualisasi satu run di samping file JSON hasilnya."""
    base = json_path.with_suffix("")
    title = json_path.stem
    plot_state(r.initial_state, f"{title}: initial state", Path(f"{base}_initial.png"), show)
    plot_state(r.final_state, f"{title}: final state", Path(f"{base}_final.png"), show)

    if "avg_history" in r.extra:
        plot_history(r.history, f"{title}: objective vs iterasi",
                     {"rata-rata populasi": r.extra["avg_history"]},
                     Path(f"{base}_history.png"), label="objective maksimum", show=show)
    elif "best_history" in r.extra:
        plot_history(r.history, f"{title}: objective vs iterasi",
                     {"best so far": r.extra["best_history"]},
                     Path(f"{base}_history.png"), show=show)
    else:
        plot_history(r.history, f"{title}: objective vs iterasi",
                     save_to=Path(f"{base}_history.png"), show=show)

    if "acceptance_probability" in r.extra:
        plot_acceptance_probability(r.extra["acceptance_probability"],
                                    save_to=Path(f"{base}_acceptance.png"), show=show)

def main() -> None:
    args = parse_args()
    set_objective_mode(args.objective)
    truck, packages = load_problem(args.input)

    if args.ga_experiment:
        runs = run_ga_experiment(truck, packages, n_runs=args.runs, seed=args.seed)
    else:
        runs = run_repeated(args.algo, truck, packages, n_runs=args.runs, seed=args.seed,
                            **algo_params(args))
    summarize([r for r, _ in runs])

    if args.no_plot:
        return
    for r, path in runs:
        plot_result(r, path, args.show)
    print(f"Hasil dan plot disimpan di {runs[0][1].parent}")


if __name__ == "__main__":
    main()
