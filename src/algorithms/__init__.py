from .genetic import GeneticAlgorithm
from .hill_climbing import RandomRestartHC, SidewaysMoveHC, SteepestAscentHC, StochasticHC
from .simulated_annealing import SimulatedAnnealing

ALGORITHMS = {
    "steepest": SteepestAscentHC,
    "sideways": SidewaysMoveHC,
    "random_restart": RandomRestartHC,
    "stochastic": StochasticHC,
    "sa": SimulatedAnnealing,
    "ga": GeneticAlgorithm,
}
