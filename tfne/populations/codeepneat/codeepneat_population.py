from ..base_population import BasePopulation
from ...encodings.codeepneat import CoDeepNEATGenome


class CoDeepNEATPopulation(BasePopulation):
    """"""

    def __init__(self, saved_state=None):
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

        # If a saved_state was supplied, load the population from that saved state and overwrite blank defaults
        if saved_state is not None:
            self._load_population(saved_state)

    def get_best_genome(self) -> CoDeepNEATGenome:
        """"""
        raise NotImplementedError("Subclass of BasePopulation does not implement 'get_best_genome()'")

    def save_population(self, save_dir_path):
        """"""
        raise NotImplementedError("Subclass of BasePopulation does not implement 'save_population()'")

    def _load_population(self, saved_state):
        """"""
        raise NotImplementedError()
