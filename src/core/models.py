from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations

Dim = tuple[int, int, int]

ORIENTATIONS: list[Dim] = list(permutations((0, 1, 2)))

ROTATION_SWAP = {
    "x": (1, 2),
    "y": (0, 2),
    "z": (0, 1),
}

@dataclass(frozen=True)
class Package:
    id: str
    dims: Dim
    value: int
    weight: int
    is_fragile: bool
    eta: int

    def oriented_dims(self, orientation: Dim) -> Dim:
        return tuple(self.dims[i] for i in orientation)

    @property
    def volume(self) -> int:
        w, l, h = self.dims
        return w * l * h

@dataclass(frozen=True)
class Truck:
    dims: Dim
    max_capacity : int

    @property
    def volume(self) -> int:
        w, l, h = self.dims
        return w * l * h

def rotate(orientation: Dim, axis: str) -> Dim:
    a, b = ROTATION_SWAP[axis]
    o = list(orientation)
    o[a], o[b] = o[b], o[a]
    return tuple(o)