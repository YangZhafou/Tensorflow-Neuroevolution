import statistics

from ..base_population import BasePopulation


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

    def summarize_population(self):
        """"""
        # Determine average fitness of all blueprints
        bp_fitness_list = [self.blueprints[bp_id].get_fitness() for bp_id in self.blueprints]
        blueprints_avg_fitness = round(statistics.mean(bp_fitness_list), 4)

        # Determine best id of each blueprint species
        bp_species_best_id = dict()
        for spec_id, spec_bp_ids in self.bp_species.items():
            spec_bp_ids_sorted = sorted(spec_bp_ids, key=lambda x: self.blueprints[x].get_fitness(), reverse=True)
            bp_species_best_id[spec_id] = spec_bp_ids_sorted[0]

        # Determine average fitness of all modules
        mod_fitness_list = [self.modules[mod_id].get_fitness() for mod_id in self.modules]
        modules_avg_fitness = round(statistics.mean(mod_fitness_list), 4)

        # Determine best id of each module species
        mod_species_best_id = dict()
        for spec_id, spec_mod_ids in self.mod_species.items():
            spec_mod_ids_sorted = sorted(spec_mod_ids, key=lambda x: self.modules[x].get_fitness(), reverse=True)
            mod_species_best_id[spec_id] = spec_mod_ids_sorted[0]

        # Print summary header
        print("\n\n\n\033[1m{}  Population Summary  {}\n\n"
              "Generation: {:>4}  ||  Best Genome Fitness: {:>8}  ||  Avg Blueprint Fitness: {:>8}  ||  "
              "Avg Module Fitness: {:>8}\033[0m\n"
              "Best Genome: {}\n"
              .format('#' * 60,
                      '#' * 60,
                      self.generation_counter,
                      self.best_fitness,
                      blueprints_avg_fitness,
                      modules_avg_fitness,
                      self.best_genome))

        # Print summary of blueprint species
        print("\033[1mBlueprint Species       || Blueprint Species Avg Fitness       || Blueprint Species Size\033[0m")
        for spec_id, spec_fitness_hisotry in self.bp_species_fitness_history.items():
            print("{:>6}                  || {:>8}                            || {:>8}"
                  .format(spec_id,
                          spec_fitness_hisotry[self.generation_counter],
                          len(self.bp_species[spec_id])))
            print(f"Best BP of Species {spec_id}    || {self.blueprints[bp_species_best_id[spec_id]]}")

        # Print summary of module species
        print("\n\033[1mModule Species          || Module Species Avg Fitness          || Module Species Size\033[0m")
        for spec_id, spec_fitness_hisotry in self.mod_species_fitness_history.items():
            print("{:>6}                  || {:>8}                            || {:>8}"
                  .format(spec_id,
                          spec_fitness_hisotry[self.generation_counter],
                          len(self.mod_species[spec_id])))
            print(f"Best Mod of Species {spec_id}   || {self.modules[mod_species_best_id[spec_id]]}")

        # Print summary footer
        print("\n\033[1m" + '#' * 142 + "\033[0m\n")

    def save_population(self, save_dir_path):
        """"""
        raise NotImplementedError("Subclass of BasePopulation does not implement 'save_population()'")

    def _load_population(self, saved_state):
        """"""
        raise NotImplementedError()
