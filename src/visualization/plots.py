from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from core.objective import objective
from core.state import State

def plot_history(history: list[float], title: str = "Objective vs Iterasi",
                 extra_series: dict[str, list[float]] | None = None,
                 save_to: Path | None = None) -> None:
    """Plot objective terhadap iterasi. `extra_series` untuk mis. rata-rata populasi GA."""
    plt.figure(figsize=(8, 4))
    plt.plot(history, label="objective")
    for label, series in (extra_series or {}).items():
        plt.plot(series, label=label)
    plt.xlabel("Iterasi"); plt.ylabel("Objective"); plt.title(title); plt.legend()
    plt.tight_layout()
    if save_to:
        plt.savefig(save_to, dpi=150)
    plt.show()

