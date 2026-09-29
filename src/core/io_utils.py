from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from .models import Package, Truck

OUTPUT_DIR = Path(__file__).resolve().parents[2] / "output"


def _dims(d: dict) -> tuple[int, int, int]:
    return (int(d["w"]), int(d["l"]), int(d["h"]))


def load_problem(path: str | Path) -> tuple[Truck, dict[str, Package]]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    truck = Truck(dims=_dims(data["truck"]["dimensions"]),
                  max_capacity=int(data["truck"]["max_capacity"]))
    packages = {
        p["id"]: Package(
            id=p["id"],
            dims=_dims(p["dimensions"]),
            value=int(p["value"]),
            weight=int(p["weight"]),
            is_fragile=bool(p["is_fragile"]),
            eta=int(p["eta"]),
        )
        for p in data["packages"]
    }
    return truck, packages


def save_result(result: dict, name: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = OUTPUT_DIR / f"{name}_{stamp}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    return path
