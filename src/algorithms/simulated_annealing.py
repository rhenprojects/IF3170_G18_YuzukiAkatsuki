from __future__ import annotations
from typing import Any

from core.evaluator import NeighborEvaluator
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
        cooling_rate: float | None = None,
        min_temp: float = 0.001,
        max_iterations: int = 5000,
        stuck_patience: int = 100,
        seed: int | None = None,
    ):
        super().__init__(seed)
        self.initial_temp = initial_temp
        self.min_temp = min_temp
        self.max_iterations = max_iterations
        self.cooling_rate = (cooling_rate if cooling_rate is not None
                             else (min_temp / initial_temp) ** (1 / max_iterations))
        self.stuck_patience = stuck_patience

    def schedule(self, t: int) -> float:
        return self.initial_temp * (self.cooling_rate ** t)

    @staticmethod
    def acceptance_probability(delta_e: float, temp: float) -> float:
        if delta_e > 0:
            return 1.0
        return math.exp(delta_e / temp) if temp > 0 else 0.0

    def _search(self, initial: State) -> tuple[State, int, list[float], dict[str, Any]]:
        current, current_val = initial, objective(initial)
        evaluator = NeighborEvaluator(current)
        best, best_val = current, current_val
        history = [current_val]
        best_history = [best_val]
        prob_history: list[float] = []
        stuck_events: list[tuple[int, float]] = []
        stuck_iterations = 0
        rejected_valid = 0
        rejected_invalid = 0
        unchanged_streak = 0
        iterations = 0

        for t in range(self.max_iterations):
            temp = self.schedule(t)
            if temp < self.min_temp:
                break

            try:
                move = random_move(current, self.rng)
            except ValueError:
                break

            neighbor_val = evaluator.evaluate(move)
            delta_e = neighbor_val - current_val
            p = self.acceptance_probability(delta_e, temp)
            prob_history.append(p)
            iterations += 1

            previous_val = current_val
            if self.rng.random() < p:
                current, current_val = apply_move(current, move), neighbor_val
                evaluator = NeighborEvaluator(current)
                if current_val > best_val:
                    best, best_val = current, current_val
            elif neighbor_val < 0:
                rejected_invalid += 1
            else:
                rejected_valid += 1

            if current_val == previous_val:
                unchanged_streak += 1
                if unchanged_streak == self.stuck_patience:
                    stuck_events.append((iterations, temp))
                if unchanged_streak >= self.stuck_patience:
                    stuck_iterations += 1
            else:
                unchanged_streak = 0

            history.append(current_val)
            best_history.append(best_val)

        return best, iterations, history, {
            "acceptance_probability": prob_history,
            "best_history": best_history,
            "stuck_count": len(stuck_events),
            "stuck_events": stuck_events,
            "stuck_iterations": stuck_iterations,
            "stuck_patience": self.stuck_patience,
            "rejected_valid": rejected_valid,
            "rejected_invalid": rejected_invalid,
        }