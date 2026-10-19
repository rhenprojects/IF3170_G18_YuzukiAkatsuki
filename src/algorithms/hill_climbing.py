from __future__ import annotations
from typing import Any

from core.evaluator import NeighborEvaluator
from core.neighbors import all_moves, apply_move, random_move
from core.objective import objective
from core.state import State
from .base import LocalSearch

def best_neighbor(state: State) -> tuple[State | None, float]:
    evaluator = NeighborEvaluator(state)
    best_move, best_val = None, float("-inf")
    for move in all_moves(state):
        val = evaluator.evaluate(move)
        if val > best_val:
            best_move, best_val = move, val
    if best_move is None:
        return None, best_val
    return apply_move(state, best_move), best_val

class SteepestAscentHC(LocalSearch):
    name = "steepest_ascent_hc"

    def _search(self, initial: State) -> tuple[State, int, list[float], dict[str, Any]]:
        current, current_val = initial, objective(initial)
        history = [current_val]
        iterations = 0
        while True:
            neighbor, val = best_neighbor(current)
            if val <= current_val:
                break

            current = neighbor
            current_val = val

            iterations += 1
            history.append(current_val)

        return current, iterations, history, {}


class SidewaysMoveHC(LocalSearch):
    name = "sideways_move_hc"

    def __init__(self, max_sideways: int = 100, seed: int | None = None):
        super().__init__(seed)
        self.max_sideways = max_sideways

    def _search(self, initial):
        current, current_val = initial, objective(initial)
        history = [current_val]
        iterations = 0
        sideways_count = 0
        while True:
            neighbor, val = best_neighbor(current)
            if val < current_val:
                break

            if val == current_val:
                if sideways_count >= self.max_sideways:
                    break
                sideways_count+=1

            current = neighbor
            current_val = val

            iterations += 1
            history.append(current_val)

        return current, iterations, history, {}

class RandomRestartHC(LocalSearch):
    name = "random_restart_hc"

    def __init__(self, max_restart: int = 10, seed: int | None = None):
        super().__init__(seed)
        self.max_restart = max_restart

    def _search(self, initial: State) -> tuple[State, int, list[float], dict[str, Any]]:
        best, best_val = initial, objective(initial)
        history = []
        best_history = []
        iterations_per_restart = []
        restart_at = []  # indeks history tempat restart dimulai (untuk plot)

        for attempt in range(self.max_restart + 1):
            if attempt == 0:
                current = initial
            else:
                current = State.random_initial(initial.truck, initial.packages, self.rng)
                restart_at.append(len(history))
            current_val = objective(current)
            history.append(current_val)
            best_history.append(max(best_val, current_val))
            iterations = 0

            while True:
                neighbor, val = best_neighbor(current)
                if val <= current_val:
                    break

                current = neighbor
                current_val = val

                iterations += 1
                history.append(current_val)
                best_history.append(max(best_history[-1], current_val))

            iterations_per_restart.append(iterations)
            if current_val > best_val:
                best, best_val = current, current_val

        extra = {
            "restarts": self.max_restart,
            "iterations_per_restart": iterations_per_restart,
            "restart_at": restart_at,
            "best_history": best_history,
        }
        return best, sum(iterations_per_restart), history, extra


class StochasticHC(LocalSearch):
    name = "stochastic_hc"

    def __init__(self, max_iterations: int = 10_000, seed: int | None = None):
        super().__init__(seed)
        self.max_iterations = max_iterations

    def _search(self, initial: State) -> tuple[State, int, list[float], dict[str, Any]]:
        current, current_val = initial , objective(initial)
        evaluator = NeighborEvaluator(current)
        history = [current_val]
        accepted = 0
        iterations = 0

        for _ in range(self.max_iterations):
            try:
                move = random_move(current, self.rng)
            except ValueError:
                # tidak ada neighbor yang mengubah state
                break
            iterations += 1
            val = evaluator.evaluate(move)
            if val > current_val:
                current, current_val = apply_move(current, move), val
                evaluator = NeighborEvaluator(current)
                accepted += 1
            history.append(current_val)

        return current, iterations, history, {"accepted_moves": accepted}
