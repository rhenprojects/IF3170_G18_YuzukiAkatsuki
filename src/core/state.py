from __future__ import annotations

import random
from dataclasses import dataclass, field

from .models import ORIENTATIONS, Dim, Package, Truck

@dataclass
class Placement:
    position: Dim | None = None
    orientation: Dim = (0, 1, 2)

    @property
    def inside(self) -> bool:
        return self.position is not None

@dataclass
class State:
    truck: Truck
    packages: dict[str, Package]
    placements: dict[str, Placement] = field(default_factory=dict)

    def copy(self) -> "State":
        return State(
            truck= self.truck,
            packages=self.packages,
            placements={
                pid: Placement(p.position, p.orientation)
                for pid, p in self.placements.items()
            },
        )

    def inside_ids(self) -> list[str]:
        return [pid for pid, p in self.placements.items() if p.inside]

    def outside_ids(self) -> list[str]:
        return [pid for pid, p in self.placements.items() if not p.inside]

    def box(self, pid: str) -> tuple[Dim, Dim]:
        pl = self.placements[pid]
        assert pl.position is not None, f"{pid} berada di luar truk"
        return pl.position, self.packages[pid].oriented_dims(pl.orientation)

    @classmethod
    def random_initial(
        cls,
        truck: Truck,
        packages: dict[str, Package],
        rng: random.Random | None = None,
    ) -> "State":
        """TODO: Apakah perlu di pilih orientasi yang muat kalo tidak muat?"""
        rng = rng or random.Random()
        state = cls(truck=truck, packages=packages)
        truck_w, truck_d, truck_h = truck.dims

        for pid, package in packages.items():
            # pilih orientasi random
            orientation = rng.choice(ORIENTATIONS)

            # dimensi paket setelah di orientasikan
            w, d, h = package.oriented_dims(orientation)

            if w > truck_w or d > truck_d or h > truck_h:
                state.placements[pid] = Placement(position=None, orientation=orientation,)
                continue

            # paket random bisa di luar atau di dalam

            if rng.random() < 0.5:
                x = rng.randint(0, truck_w-w)
                y = rng.randint(0, truck_d-d)
                z = rng.randint(0, truck_h-h)   
                position = (x, y, z)

            else:
                position = None

            state.placements[pid] = Placement(position=position, orientation=orientation)
        return state
    
    @classmethod
    def from_dict(cls, truck: Truck, packages: dict[str, Package], data: dict) -> "State":
        """Kebalikan to_dict: bangun ulang state dari hasil run yang disimpan."""
        state = cls(truck, packages)
        state.placements = {
            pid: Placement(position=tuple(p["position"]) if p["position"] is not None else None,
                           orientation=tuple(p["orientation"]))
            for pid, p in data.items()
        }
        return state

    def to_dict(self) -> dict:
        return {
            pid: {
                "inside": pl.inside,
                "position": list(pl.position) if pl.position else None,
                "orientation": list(pl.orientation),
                "oriented_dims": list(self.packages[pid].oriented_dims(pl.orientation)),
            }
            for pid, pl in self.placements.items()
        }