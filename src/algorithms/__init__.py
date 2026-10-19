from .genetic import GeneticAlgorithm
from .hill_climbing import SteepestAscentHC
from .simulated_annealing import SimulatedAnnealing

ALGORITHMS = {
    "steepest": SteepestAscentHC,
    "sa": SimulatedAnnealing,
    "ga": GeneticAlgorithm,
    # TODO: buat hc
    #   "sideways": SidewaysMoveHC,
    #   "random_restart": RandomRestartHC,
    #   "stochastic": StochasticHC,
}
