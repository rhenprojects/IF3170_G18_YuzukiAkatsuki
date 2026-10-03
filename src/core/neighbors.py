from __future__ import annotations

import random
from collections.abc import Iterator
from dataclasses import dataclass

from .models import Dim, rotate
from .state import State

@dataclass(frozen=True)
class Move:
    kind: str # "swap" | "move" | "rotate"
    a: str # id paket
    b: str | None = None # id paket kedua kalo swap
    position: Dim | None = None # target koordinat kalo move, None = keluarkan dari Truk
    axis: str | None = None # "x" | "y" | "z"

def apply_move(state: State, move: Move) -> State:
    new = state.copy()
    pa = new.placements[move.a]

    if move.kind == "swap":
        pb = new.placements[move.b]
        # tukar posisi saja, orientasi tetap
        pa.position, pb.position = pb.position, pa.position
    elif move.kind == "move":
        pa.position = move.position
    elif move.kind == "rotate":
        pa.orientation = rotate(pa.orientation, move.axis)
    else:
        raise ValueError(f"Move tidak dikenal: {move.kind}")
    return new

def is_noop(state: State, move: Move) -> bool:
    """True jika move tidak mengubah state (tidak dihitung sebagai neighbor)."""
    pa = state.placements[move.a]

    if move.kind == "swap":
        # posisi sama (termasuk sama-sama di luar truk) -> tidak ada perubahan
        return pa.position == state.placements[move.b].position
    if move.kind == "move":
        return pa.position == move.position
    if move.kind == "rotate":
        # rotasi paket di luar truk tidak berpengaruh, begitu juga rotasi
        # yang menghasilkan dimensi sama (contoh sisi w == l saat rotasi z)
        if not pa.inside:
            return True
        package = state.packages[move.a]
        return (package.oriented_dims(rotate(pa.orientation, move.axis))
                == package.oriented_dims(pa.orientation))
    raise ValueError(f"Move tidak dikenal: {move.kind}")

def candidate_positions(state: State, pid: str) -> list[Dim]:
    truck_w, truck_d, truck_h = state.truck.dims

    package = state.packages[pid]
    orientation = state.placements[pid].orientation
    w, d, h = package.oriented_dims(orientation)

    candidates: set[Dim] = set()

    # Kalau paket lebih besar dari truck dalam orientasi ini,
    # tidak ada posisi valid di dalam truck.
    if w > truck_w or d > truck_d or h > truck_h:
        return []

    # Pojok/lantai truck
    candidates.add((0, 0, 0))

    # Extreme points berdasarkan paket lain
    for other in state.inside_ids():
        if other == pid:
            continue

        (x, y, z), (ow, od, oh) = state.box(other)

        # Di sebelah kanan paket
        candidates.add((x + ow, y, z))

        # Di depan paket
        candidates.add((x, y + od, z))

        # Di atas paket
        candidates.add((x, y, z + oh))

        # Kombinasi pojok
        candidates.add((x + ow, y + od, z))
        candidates.add((x + ow, y, z + oh))
        candidates.add((x, y + od, z + oh))
        candidates.add((x + ow, y + od, z + oh))

    # Batasi hanya posisi yang seluruh box-nya berada di dalam truck
    valid_candidates = []

    for x, y, z in candidates:
        if (
            0 <= x
            and x + w <= truck_w
            and 0 <= y
            and y + d <= truck_d
            and 0 <= z
            and z + h <= truck_h
        ):
            valid_candidates.append((x, y, z))

    return valid_candidates

def all_moves(state: State) -> Iterator[Move]:
    """Enumerasi seluruh neighbor (dipakai steepest ascent / sideways / random restart)."""
    for move in _all_moves_raw(state):
        if not is_noop(state, move):
            yield move

def _all_moves_raw(state: State) -> Iterator[Move]:
    ids = list(state.placements)
    # swap
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            yield Move("swap", a, b=b)
    # rotate
    for a in ids:
        for axis in ("x", "y", "z"):
            yield Move("rotate", a, axis=axis)
    # move
    for a in ids:
        for pos in candidate_positions(state, a):
            yield Move("move", a, position=pos)
        if state.placements[a].inside:
            yield Move("move", a, position=None)  # keluarkan dari truk

def random_move(state: State, rng: random.Random, max_tries: int = 100) -> Move:
    """Ambil satu neighbor secara acak (move yang tidak mengubah state dilewati)."""
    ids = list(state.placements)

    if not ids:
        raise ValueError("State tidak memiliki paket.")

    for _ in range(max_tries):
        kind = rng.choice(("swap", "move", "rotate"))

        # swap
        if kind == "swap":
            if len(ids) < 2:
                continue
            a, b = rng.sample(ids, 2)
            move = Move(kind="swap", a=a, b=b)

        # move
        elif kind == "move":
            a = rng.choice(ids)
            candidates = candidate_positions(state, a)

            # Paket bisa dikeluarkan dari truck
            if state.placements[a].inside:
                candidates.append(None)

            if not candidates:
                continue
            move = Move(kind="move", a=a, position=rng.choice(candidates))

        # rotate (hanya berpengaruh untuk paket di dalam truk)
        else:
            inside = state.inside_ids()
            if not inside:
                continue
            move = Move(kind="rotate", a=rng.choice(inside),
                        axis=rng.choice(("x", "y", "z")))

        if not is_noop(state, move):
            return move

    raise ValueError("Tidak ditemukan neighbor yang mengubah state.")
