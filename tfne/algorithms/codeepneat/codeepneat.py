import tfne
from ..base_algorithm import BaseNeuroevolutionAlgorithm
from ...encodings.codeepneat import CoDeepNEATGenome

from ._config_processing import ConfigProcessing


class CoDeepNEAT(BaseNeuroevolutionAlgorithm,
                 ConfigProcessing):
    """"""

    def __init__(self, config, environment, initial_population_file_path=None):
        """"""
        # Read and process the supplied config and register the optionally supplied initial population
        self.process_config(config)
        self.initial_population_file_path = initial_population_file_path

        # Register the supplied environment class and declare the container for the initialized evaluation environments
        # as well as the environment parameters (input and output dimension/shape) to which the created neural networks
        # have to adhere to and which will be set when initializing the environments.
        self.environment = environment
        self.envs = list()
        self.input_shape = None
        self.input_dim = None
        self.output_shape = None
        self.output_dim = None

        # Initialize and register the associated CoDeepNEAT encoding
        self.encoding = tfne.encodings.CoDeepNEATEncoding(dtype=self.dtype)

        # Declare internal variables of the population
        self.generation_counter = None
        self.best_genome = None
        self.best_fitness = None

        # Declare and initialize internal variables concerning the module population of the CoDeepNEAT algorithm
        self.modules = dict()
        self.mod_species = dict()
        self.mod_species_repr = dict()
        self.mod_species_type = dict()
        self.mod_species_counter = 0

        # Declare and initialize internal variables concerning the blueprint population of the CoDeepNEAT algorithm
        self.blueprints = dict()
        self.bp_species = dict()
        self.bp_species_repr = dict()
        self.bp_species_counter = 0

        print('CLEAN EXIT')
        exit()

    def initialize_environments(self, num_cpus, num_gpus, verbosity):
        """"""
        pass

    def initialize_population(self):
        """"""
        pass

    def evaluate_population(self) -> (int, int):
        """"""
        pass

    def summarize_population(self):
        """"""
        pass

    def evolve_population(self) -> bool:
        """"""
        pass

    def save_population(self, save_dir_path):
        """"""
        pass

    def get_best_genome(self) -> CoDeepNEATGenome:
        """"""
        return self.best_genome
