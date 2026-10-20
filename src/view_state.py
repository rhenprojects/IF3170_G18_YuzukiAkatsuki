"""Buka ulang state hasil run dalam plot 3D interaktif yang bisa diputar 360 derajat.

Contoh (dari folder src):
    python view_state.py --input ../data/medium_input.json --result ../output/<hasil>.json
    python view_state.py --input ../data/medium_input.json --result ../output/<hasil>.json --which initial
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from core.io_utils import load_problem
from core.objective import set_objective_mode
from core.state import State
from visualization.plots import plot_state


def main() -> None:
    p = argparse.ArgumentParser(description="Visualisasi 3D state hasil run")
    p.add_argument("--input", required=True, help="File JSON problem yang dipakai saat run")
    p.add_argument("--result", required=True, help="File JSON hasil run di folder output")
    p.add_argument("--which", choices=("initial", "final"), default="final")
    args = p.parse_args()

    truck, packages = load_problem(args.input)
    result_path = Path(args.result)
    with open(result_path, encoding="utf-8") as f:
        result = json.load(f)
    if set(result[f"{args.which}_state"]) != set(packages):
        p.error("paket di --result tidak sama dengan paket di --input")

    set_objective_mode(result.get("objective_mode", "value"))
    state = State.from_dict(truck, packages, result[f"{args.which}_state"])
    plot_state(state, f"{result_path.stem}: {args.which} state", show=True)


if __name__ == "__main__":
    main()
