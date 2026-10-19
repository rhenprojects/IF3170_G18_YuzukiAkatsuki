from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from core.objective import count_violations, is_valid, objective, total_value, total_weight
from core.state import State


def _cuboid_faces(pos, dims):
    x, y, z = pos
    w, l, h = dims
    v = [(x, y, z), (x + w, y, z), (x + w, y + l, z), (x, y + l, z),
         (x, y, z + h), (x + w, y, z + h), (x + w, y + l, z + h), (x, y + l, z + h)]
    return [[v[0], v[1], v[2], v[3]], [v[4], v[5], v[6], v[7]],
            [v[0], v[1], v[5], v[4]], [v[2], v[3], v[7], v[6]],
            [v[1], v[2], v[6], v[5]], [v[0], v[3], v[7], v[4]]]


def plot_state(state: State, title: str = "", save_to: Path | None = None) -> None:
    fig = plt.figure(figsize=(11, 5.5))
    ax = fig.add_subplot(121, projection="3d")
    W, L, H = state.truck.dims
    ax.set_xlim(0, W); ax.set_ylim(0, L); ax.set_zlim(0, H)
    ax.set_box_aspect((W, L, H))
    ax.set_xlabel("w (x)"); ax.set_ylabel("l (y)"); ax.set_zlabel("h (z)")

    # warna tetap per paket (berdasarkan urutan id) agar sama di state awal dan akhir
    color_of = {pid: i for i, pid in enumerate(sorted(state.packages))}
    cmap = plt.get_cmap("tab20")
    for pid in state.inside_ids():
        pos, dims = state.box(pid)
        ax.add_collection3d(Poly3DCollection(
            _cuboid_faces(pos, dims), alpha=0.55, edgecolor="k", linewidths=0.4,
            facecolor=cmap(color_of[pid] % 20),
            hatch="///" if state.packages[pid].is_fragile else None,
        ))
    ax.set_title(title, fontsize=10)

    # ringkasan state dan paket di luar truk
    ax2 = fig.add_subplot(122); ax2.axis("off")
    outside = sorted(state.outside_ids())
    lines = [
        f"Objective       : {objective(state):.2f}",
        f"Total value     : {total_value(state)}",
        f"Berat/kapasitas : {total_weight(state)}/{state.truck.max_capacity}",
        f"Paket di dalam  : {len(state.inside_ids())}/{len(state.placements)}",
        f"Valid           : {'ya' if is_valid(state) else 'tidak'}",
        "",
        "Pelanggaran:",
        *(f"  {k}: {v}" for k, v in count_violations(state).items()),
        "",
        "Di luar truk (arsir = fragile):",
        "  " + (", ".join(outside) if outside else "-"),
    ]
    ax2.text(0, 1, "\n".join(lines), va="top", family="monospace", fontsize=9, wrap=True)

    fig.tight_layout()
    if save_to:
        fig.savefig(save_to, dpi=150, bbox_inches="tight")
    plt.show()

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

def plot_acceptance_probability(probabilities: list[float],
                                title: str = "Peluang penerimaan e^(ΔE/T) vs Iterasi",
                                save_to: Path | None = None) -> None:
    """Plot peluang menerima langkah di tiap iterasi (1.0 untuk langkah yang tidak memperburuk)."""
    plt.figure(figsize=(8, 4))
    plt.scatter(range(1, len(probabilities) + 1), probabilities, s=3)
    plt.ylim(-0.05, 1.05)
    plt.xlabel("Iterasi"); plt.ylabel("e^(ΔE/T)"); plt.title(title)
    plt.tight_layout()
    if save_to:
        plt.savefig(save_to, dpi=150)
    plt.show()