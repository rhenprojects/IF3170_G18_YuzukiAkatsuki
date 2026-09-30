from __future__ import annotations

from .state import State

PENALTY_WEIGHTS = {
    "out_of_bounds": 1,
    "overlap": 1,
    "floating": 1,
    "fragile_support": 1,
    "overweight": 1,
}

# agar value ketika ada pelanggaran selalu lebih buruk dibandingkan tidak ada
def penalty_scale(state: State) -> int:
    return sum(p.value for p in state.packages.values()) + 1

def is_within_truck(state: State, pid: str) -> bool:
    pl = state.placements[pid]

    if pl.position is None:
        return False
    
    truck_w, truck_d, truck_h = state.truck.dims
    (x, y, z), (w, d, h) = state.box(pid)
    return (x >= 0 and x + w <= truck_w and y >= 0 and y + d <= truck_d
            and z >= 0 and z + h <= truck_h)

def overlaps(state: State, a: str, b: str) -> bool:
    if not state.placements[a].inside or not state.placements[b].inside:
        return False

    (x1, y1, z1), (w1, d1, h1) = state.box(a)
    (x2, y2, z2), (w2, d2, h2) = state.box(b)

    return not (x1 + w1 <= x2 or x2 + w2 <= x1
            or y1 + d1 <= y2 or y2 + d2 <= y1
            or z1 + h1 <= z2 or z2 + h2 <= z1)

def supporters(state: State, pid: str) -> list[str]:
    if not state.placements[pid].inside:
        return []
    
    (xi, yi, zi), (wi, di, hi) = state.box(pid)

    result = []

    for other in state.inside_ids():
        if other == pid:
            continue
        
        (xj, yj, zj), (wj, dj, hj) = state.box(other)

        if zj + hj != zi:
            continue

        x_overlap = (
            xi < xj + wj
            and xj < xi + wi
        )

        y_overlap = (
            yi < yj + dj
            and yj < yi + di
        )

        if x_overlap and y_overlap:
            result.append(other)

    return result

def is_floating(state: State, pid: str) -> bool:
    if not state.placements[pid].inside:
        return False
    
    _, _, zi = state.placements[pid].position

    if zi == 0:
        return False

    return len(supporters(state, pid)) == 0

def total_weight(state: State) -> int:
    return sum(state.packages[pid].weight for pid in state.inside_ids())


def total_value(state: State) -> int:
    return sum(state.packages[pid].value for pid in state.inside_ids())        


def count_violations(state: State) -> dict[str, int]:
    inside = state.inside_ids()

    # paket di dalam yang menembus truk
    out_of_bounds = sum(not is_within_truck(state, pid) for pid in inside)

    # hitung yg overlap
    overlap = 0

    for i in range(len(inside)):
        for j in range(i+1, len(inside)):
            if overlaps(state, inside[i], inside[j]):
                overlap +=1

    # supporters tiap paket dihitung sekali, dipakai untuk cek melayang dan fragile
    sup = {pid: supporters(state, pid) for pid in inside}

    # hitung melayang
    floating = sum(
        state.placements[pid].position[2] != 0 and not sup[pid]
        for pid in inside
    )

    # paket fragile yang jadi support
    fragile_support = sum(
        state.packages[s].is_fragile
        for pid in inside
        for s in sup[pid]
    )

    # berat melebihi kapasitas
    overweight = max(0, total_weight(state) - state.truck.max_capacity)

    return {
        "out_of_bounds": out_of_bounds,
        "overlap": overlap,
        "floating": floating,
        "fragile_support": fragile_support,
        "overweight": overweight,
    }

def is_valid(state: State) -> bool:
    return all(v == 0 for v in count_violations(state).values())

def objective(state: State) -> float:
    violations = count_violations(state)
    scale = penalty_scale(state)
    penalty = sum(scale * PENALTY_WEIGHTS[k] * v for k, v in violations.items())
    return total_value(state) - penalty