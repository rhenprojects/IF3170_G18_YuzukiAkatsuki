from __future__ import annotations
from typing import Any

from core.neighbors import apply_move, random_move
from core.objective import objective
from core.state import State
from .base import LocalSearch

import math

class SimulatedAnnealing(LocalSearch):
    name = "simulated_annealing"

    def __init__(
        self,
        initial_temp: float = 1000.0,
        cooling_rate: float = 0.995,
        min_temp: float = 0.001,
        max_iterations: int = 100000,
        seed: int | None = None,
    ):
        super().__init__(seed)
        self.initial_temp = initial_temp
        self.cooling_rate = cooling_rate
        self.min_temp = min_temp
        self.max_iterations = max_iterations

    def schedule(self, t: int) -> float:
        return self.initial_temp * (self.cooling_rate ** t)

    @staticmethod
    def acceptance_probability(delta_e: float, temp: float) -> float:
        if delta_e > 0:
            return 1.0
        return math.exp(delta_e / temp) if temp > 0 else 0.0

    def _search(self, initial: State) -> tuple[State, int, list[float], dict[str, Any]]:
        current, current_val = initial, objective(initial)
        history = [current_val]
        prob_history: list[float] = []  
        stuck_count = 0
        iterations = 0
        # TODO:
        # for t in range(max_iterations):
        #   T = schedule(t); if T < min_temp: break
        #   neighbor = apply_move(current, random_move(current, self.rng))
        #   ΔE = objective(neighbor) - current_val
        #   p = acceptance_probability(ΔE, T); prob_history.append(p)
        #   if ΔE > 0 or rng.random() < p: terima neighbor
        #   kondisi 'stuck'
        raise NotImplementedError
        return current, iterations, history, {
            "acceptance_probability": prob_history,
            "stuck_count": stuck_count,
        }
