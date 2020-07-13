from ..base_population import BasePopulation
from ...encodings.codeepneat import CoDeepNEATGenome


class CoDeepNEATPopulation(BasePopulation):
    """"""

    def __init__(self, saved_population_file_path=None):
        """"""
        # Declare internal variables of the CoDeepNEAT population
        self.generation_counter = None
        self.best_genome = None
        self.best_fitness = None

        # Declare and initialize internal variables concerning the module population of the CoDeepNEAT algorithm
        self.modules = dict()
        self.mod_species = dict()
        self.mod_species_repr = dict()
        self.mod_species_fitness_history = dict()
        self.mod_species_counter = 0

        # Declare and initialize internal variables concerning the blueprint population of the CoDeepNEAT algorithm
        self.blueprints = dict()
        self.bp_species = dict()
        self.bp_species_repr = dict()
        self.bp_species_fitness_history = dict()
        self.bp_species_counter = 0

        # If a file path to a saved population is supplied, load and deserialize it
        if saved_population_file_path is not None:
            raise NotImplementedError()

    def get_best_genome(self) -> CoDeepNEATGenome:
        """"""
        raise NotImplementedError("Subclass of BasePopulation does not implement 'get_best_genome()'")

    def save_population(self, save_dir_path):
        """"""
        raise NotImplementedError("Subclass of BasePopulation does not implement 'save_population()'")
