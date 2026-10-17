from .hill_climbing import SteepestAscentHC
from .simulated_annealing import SimulatedAnnealing

ALGORITHMS = {
    "steepest": SteepestAscentHC,
    "sa": SimulatedAnnealing,
    # TODO: buat hc sama ga
    #   "sideways": SidewaysMoveHC,
    #   "random_restart": RandomRestartHC,
    #   "stochastic": StochasticHC,
    #   "ga": GeneticAlgorithm,
}
