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
        