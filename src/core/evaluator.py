from __future__ import annotations

from .models import Dim, rotate
from .neighbors import Move
from .objective import PENALTY_WEIGHTS, count_violations, penalty_scale, supporters
from .state import State

Box = tuple[Dim, Dim]


def _out_of_bounds(box: Box, truck_dims: Dim) -> bool:
    (x, y, z), (w, d, h) = box
    tw, td, th = truck_dims
    return not (x >= 0 and x + w <= tw and y >= 0 and y + d <= td and z >= 0 and z + h <= th)


def _overlap(a: Box, b: Box) -> bool:
    (x1, y1, z1), (w1, d1, h1) = a
    (x2, y2, z2), (w2, d2, h2) = b
    return not (x1 + w1 <= x2 or x2 + w2 <= x1
                or y1 + d1 <= y2 or y2 + d2 <= y1
                or z1 + h1 <= z2 or z2 + h2 <= z1)


def _supports(lower: Box, upper: Box) -> bool:
    (xl, yl, zl), (wl, dl, hl) = lower
    (xu, yu, zu), (wu, du, _) = upper
    return (zl + hl == zu
            and xu < xl + wl and xl < xu + wu
            and yu < yl + dl and yl < yu + du)


class NeighborEvaluator:
    def __init__(self, state: State):
        self.state = state
        self.scale = penalty_scale(state)
        self.inside = state.inside_ids()
        self.boxes: dict[str, Box] = {pid: state.box(pid) for pid in self.inside}
        self.sup_count = {pid: len(supporters(state, pid)) for pid in self.inside}
        self.violations = count_violations(state)
        self.value = sum(state.packages[pid].value for pid in self.inside)
        self.weight = sum(state.packages[pid].weight for pid in self.inside)

    def _new_boxes(self, move: Move) -> dict[str, Box | None]:
        pls, pkgs = self.state.placements, self.state.packages
        pa = pls[move.a]

        def box(pid: str, pos: Dim | None, orientation: Dim) -> Box | None:
            return None if pos is None else (pos, pkgs[pid].oriented_dims(orientation))

        if move.kind == "swap":
            pb = pls[move.b]
            return {move.a: box(move.a, pb.position, pa.orientation),
                    move.b: box(move.b, pa.position, pb.orientation)}
        if move.kind == "move":
            return {move.a: box(move.a, move.position, pa.orientation)}
        if move.kind == "rotate":
            return {move.a: box(move.a, pa.position, rotate(pa.orientation, move.axis))}
        raise ValueError(f"Move tidak dikenal: {move.kind}")

    def evaluate(self, move: Move) -> float:
        pkgs = self.state.packages
        truck = self.state.truck
        new = self._new_boxes(move)
        old = {pid: self.boxes.get(pid) for pid in new}
        changed = list(new)

        d = dict.fromkeys(self.violations, 0)
        d_value = d_weight = 0
        sup_delta: dict[str, int] = {}          # perubahan jumlah supporter paket lain
        new_sup = dict.fromkeys(changed, 0)     # jumlah supporter baru paket yang berubah

        for c in changed:
            ob, nb = old[c], new[c]
            pkg = pkgs[c]
            frag_c = pkg.is_fragile
            if ob is not None:
                d_value -= pkg.value; d_weight -= pkg.weight
                d["out_of_bounds"] -= _out_of_bounds(ob, truck.dims)
            if nb is not None:
                d_value += pkg.value; d_weight += pkg.weight
                d["out_of_bounds"] += _out_of_bounds(nb, truck.dims)

            # pasangan dengan paket yang tidak berubah
            for j in self.inside:
                if j in new:
                    continue
                jb = self.boxes[j]
                frag_j = pkgs[j].is_fragile
                if ob is not None:
                    d["overlap"] -= _overlap(ob, jb)
                    if _supports(ob, jb):
                        d["fragile_support"] -= frag_c
                        sup_delta[j] = sup_delta.get(j, 0) - 1
                    if _supports(jb, ob):
                        d["fragile_support"] -= frag_j
                if nb is not None:
                    d["overlap"] += _overlap(nb, jb)
                    if _supports(nb, jb):
                        d["fragile_support"] += frag_c
                        sup_delta[j] = sup_delta.get(j, 0) + 1
                    if _supports(jb, nb):
                        d["fragile_support"] += frag_j
                        new_sup[c] += 1

        # pasangan antar paket yang berubah (swap)
        if len(changed) == 2:
            a, b = changed
            for boxes, sign in ((old, -1), (new, 1)):
                ba, bb = boxes[a], boxes[b]
                if ba is None or bb is None:
                    continue
                d["overlap"] += sign * _overlap(ba, bb)
                if _supports(ba, bb):
                    d["fragile_support"] += sign * pkgs[a].is_fragile
                    if sign > 0:
                        new_sup[b] += 1
                if _supports(bb, ba):
                    d["fragile_support"] += sign * pkgs[b].is_fragile
                    if sign > 0:
                        new_sup[a] += 1

        # melayang: paket yang berubah, dan paket lain yang supporter-nya berubah
        for c in changed:
            ob, nb = old[c], new[c]
            if ob is not None:
                d["floating"] -= ob[0][2] != 0 and self.sup_count[c] == 0
            if nb is not None:
                d["floating"] += nb[0][2] != 0 and new_sup[c] == 0
        for j, delta in sup_delta.items():
            if delta and self.boxes[j][0][2] != 0:
                before = self.sup_count[j]
                d["floating"] += (before + delta == 0) - (before == 0)

        weight = self.weight + d_weight
        d["overweight"] = (max(0, weight - truck.max_capacity)
                           - self.violations["overweight"])

        penalty = sum(self.scale * PENALTY_WEIGHTS[k] * (self.violations[k] + d[k])
                      for k in self.violations)
        return self.value + d_value - penalty
