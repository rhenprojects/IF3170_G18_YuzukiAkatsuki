from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from core.objective import count_violations, get_objective_mode, is_valid, objective, total_value, total_weight
from core.state import State


def _finish(show: bool) -> None:
    if show:
        plt.show()
    else:
        plt.close()


def _cuboid_faces(pos, dims):
    x, y, z = pos
    w, l, h = dims
    v = [(x, y, z), (x + w, y, z), (x + w, y + l, z), (x, y + l, z),
         (x, y, z + h), (x + w, y, z + h), (x + w, y + l, z + h), (x, y + l, z + h)]
    return [[v[0], v[1], v[2], v[3]], [v[4], v[5], v[6], v[7]],
            [v[0], v[1], v[5], v[4]], [v[2], v[3], v[7], v[6]],
            [v[1], v[2], v[6], v[5]], [v[0], v[3], v[7], v[4]]]


DEFAULT_ELEV, DEFAULT_AZIM = 25, -60


def _draw_state(ax, state: State, title: str) -> None:
    """Gambar peti kemas dan seluruh paket di dalamnya pada sumbu 3D `ax`."""
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
    ax.view_init(elev=DEFAULT_ELEV, azim=DEFAULT_AZIM)
    ax.set_title(title, fontsize=10)


def _info_lines(state: State) -> list[str]:
    outside = sorted(state.outside_ids())
    return [
        f"Objective       : {objective(state):.2f} ({get_objective_mode()})",
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


def _add_rotation_controls(fig, ax) -> None:
    from matplotlib.widgets import Button, Slider

    fig.subplots_adjust(bottom=0.2)
    s_azim = Slider(fig.add_axes((0.08, 0.09, 0.45, 0.03)), "Azimuth", 0, 360,
                    valinit=DEFAULT_AZIM % 360, valstep=1)
    s_elev = Slider(fig.add_axes((0.08, 0.04, 0.45, 0.03)), "Elevasi", -90, 90,
                    valinit=DEFAULT_ELEV, valstep=1)
    b_spin = Button(fig.add_axes((0.62, 0.04, 0.14, 0.08)), "Putar 360°")

    def update(_=None):
        ax.view_init(elev=s_elev.val, azim=s_azim.val)
        fig.canvas.draw_idle()

    s_azim.on_changed(update)
    s_elev.on_changed(update)

    # sinkronkan slider ketika plot diputar dengan mouse
    def on_release(event):
        if event.inaxes is ax:
            s_azim.eventson = s_elev.eventson = False
            s_azim.set_val(round(ax.azim) % 360)
            s_elev.set_val(max(-90, min(90, round(ax.elev))))
            s_azim.eventson = s_elev.eventson = True

    fig.canvas.mpl_connect("button_release_event", on_release)

    timer = fig.canvas.new_timer(interval=40)
    spin = {"on": False}

    def step():
        s_azim.set_val((s_azim.val + 3) % 360)

    timer.add_callback(step)

    def toggle(_):
        spin["on"] = not spin["on"]
        b_spin.label.set_text("Berhenti" if spin["on"] else "Putar 360°")
        (timer.start if spin["on"] else timer.stop)()

    b_spin.on_clicked(toggle)
    # simpan referensi agar widget tidak dihapus garbage collector
    fig._rotation_widgets = (s_azim, s_elev, b_spin, timer)


def plot_state(state: State, title: str = "", save_to: Path | None = None, show: bool = False) -> None:
    fig = plt.figure(figsize=(11, 5.5))
    ax = fig.add_subplot(121, projection="3d")
    _draw_state(ax, state, title)

    # ringkasan state dan paket di luar truk
    ax2 = fig.add_subplot(122); ax2.axis("off")
    ax2.text(0, 1, "\n".join(_info_lines(state)), va="top", family="monospace", fontsize=9,
             wrap=True)

    fig.tight_layout()
    if save_to:
        fig.savefig(save_to, dpi=150, bbox_inches="tight")
    if show:
        _add_rotation_controls(fig, ax)
    _finish(show)


def plot_history(history: list[float], title: str = "Objective vs Iterasi",
                 extra_series: dict[str, list[float]] | None = None,
                 save_to: Path | None = None, label: str = "objective",
                 show: bool = False) -> None:
    """Plot objective terhadap iterasi. `extra_series` untuk mis. rata-rata populasi GA."""
    plt.figure(figsize=(8, 4))
    plt.plot(history, label=label)
    for name, series in (extra_series or {}).items():
        plt.plot(series, label=name)
    plt.xlabel("Iterasi"); plt.ylabel("Objective"); plt.title(title); plt.legend()
    plt.tight_layout()
    if save_to:
        plt.savefig(save_to, dpi=150)
    _finish(show)

def plot_acceptance_probability(probabilities: list[float],
                                title: str = "Peluang penerimaan e^(ΔE/T) vs Iterasi",
                                save_to: Path | None = None, show: bool = False) -> None:
    """Plot peluang menerima langkah di tiap iterasi (1.0 untuk langkah yang tidak memperburuk)."""
    plt.figure(figsize=(8, 4))
    plt.scatter(range(1, len(probabilities) + 1), probabilities, s=3)
    plt.ylim(-0.05, 1.05)
    plt.xlabel("Iterasi"); plt.ylabel("e^(ΔE/T)"); plt.title(title)
    plt.tight_layout()
    if save_to:
        plt.savefig(save_to, dpi=150)
    _finish(show)