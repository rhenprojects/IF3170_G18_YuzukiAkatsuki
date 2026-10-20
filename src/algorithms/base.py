from __future__ import annotations

import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from core.objective import get_objective_mode, objective, total_value
from core.state import State


@dataclass
class SearchResult:
    algorithm: str
    initial_state: State
    final_state: State
    initial_objective: float
    final_objective: float
    duration_s: float
    iterations: int
    history: list[float] = field(default_factory=list)   # objective per iterasi
    extra: dict[str, Any] = field(default_factory=dict)  # data khusus per algoritma
    objective_mode: str = "value"                    

    def to_dict(self) -> dict:
        return {
            "algorithm": self.algorithm,
            "objective_mode": self.objective_mode,
            "final_total_value": total_value(self.final_state),
            "initial_objective": self.initial_objective,
            "final_objective": self.final_objective,
            "duration_s": self.duration_s,
            "iterations": self.iterations,
            "history": self.history,
            "extra": self.extra,
            "initial_state": self.initial_state.to_dict(),
            "final_state": self.final_state.to_dict(),
        }


class LocalSearch(ABC):
    name = "local_search"

    def __init__(self, seed: int | None = None):
        self.rng = random.Random(seed)

    def run(self, initial: State) -> SearchResult:
        """Wrapper yang mengukur durasi; logika ada di `_search`."""
        start = time.perf_counter()
        final, iterations, history, extra = self._search(initial)
        duration = time.perf_counter() - start
        return SearchResult(
            algorithm=self.name,
            initial_state=initial,
            final_state=final,
            initial_objective=objective(initial),
            final_objective=objective(final),
            duration_s=duration,
            iterations=iterations,
            history=history,
            extra=extra,
            objective_mode=get_objective_mode(),
        )

    @abstractmethod
    def _search(self, initial: State) -> tuple[State, int, list[float], dict[str, Any]]:
        """Kembalikan (final_state, banyak_iterasi, history_objective, extra)."""
