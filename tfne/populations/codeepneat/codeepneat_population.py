import statistics

from ..base_population import BasePopulation
from ...encodings.codeepneat.codeepneat_genome import CoDeepNEATGenome
from ...encodings.codeepneat.modules.codeepneat_module_base import CoDeepNEATModuleBase
from ...encodings.codeepneat.codeepneat_blueprint import CoDeepNEATBlueprint
from ...encodings.codeepneat.codeepneat_blueprint import CoDeepNEATBlueprintNode, CoDeepNEATBlueprintConn
from ...encodings.codeepneat.codeepneat_optimizer_factory import OptimizerFactory

# Import Association dict of the module string name to its implementation class, relevant for population deserialization
from ...encodings.codeepneat.modules.codeepneat_module_association import MODULES


class CoDeepNEATPopulation(BasePopulation):
    """"""

    def __init__(self, saved_state=None, dtype=None, module_config_params=None):
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
            self._load_population(saved_state, dtype, module_config_params)

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

    def serialize(self) -> dict:
        """"""
        # Serialize all modules
        serialized_modules = dict()
        for mod_id, module in self.modules.items():
            serialized_modules[mod_id] = module.serialize()

        # Serialize all blueprints
        serialized_blueprints = dict()
        for bp_id, blueprint in self.blueprints.items():
            serialized_blueprints[bp_id] = blueprint.serialize()

        # Use serialized module and blueprint population and extend it by population internal evolution information
        serialized_population = {
            'generation_counter': self.generation_counter,
            'modules': serialized_modules,
            'mod_species': self.mod_species,
            'mod_species_repr': self.mod_species_repr if self.mod_species_repr else None,
            'mod_species_fitness_history': self.mod_species_fitness_history,
            'mod_species_counter': self.mod_species_counter,
            'blueprints': serialized_blueprints,
            'bp_species': self.bp_species,
            'bp_species_repr': self.bp_species_repr if self.bp_species_repr else None,
            'bp_species_fitness_history': self.bp_species_fitness_history,
            'bp_species_counter': self.bp_species_counter,
            'best_genome': self.best_genome.serialize(),
            'best_fitness': self.best_fitness
        }

        return serialized_population

    def _load_population(self, saved_state, dtype, module_config_params):
        """"""
        # Deserialize all saved population internal evolution information except for the modules, blueprints and best
        # genome, as they have to be deserialized
        self.generation_counter = saved_state['generation_counter']
        self.mod_species = {int(k): v for k, v in saved_state['mod_species'].items()}
        self.mod_species_repr = {int(k): v for k, v in saved_state['mod_species_repr'].items()}
        self.mod_species_fitness_history = {int(k1): {int(k2): v2 for k2, v2 in v1.items()}
                                            for k1, v1 in saved_state['mod_species_fitness_history'].items()}
        self.mod_species_counter = saved_state['mod_species_counter']
        self.bp_species = {int(k): v for k, v in saved_state['bp_species'].items()}
        self.bp_species_repr = {int(k): v for k, v in saved_state['bp_species_repr'].items()}
        self.bp_species_fitness_history = {int(k1): {int(k2): v2 for k2, v2 in v1.items()}
                                           for k1, v1 in saved_state['bp_species_fitness_history'].items()}
        self.bp_species_counter = saved_state['bp_species_counter']
        self.best_fitness = saved_state['best_fitness']

        # Deserialize modules
        for mod_id, mod_params in saved_state['modules'].items():
            self.modules[int(mod_id)] = self._deserialize_module(mod_params, dtype, module_config_params)

        # Deserialize blueprints
        for bp_id, bp_params in saved_state['blueprints'].items():
            self.blueprints[int(bp_id)] = self._deserialize_blueprint(bp_params)

        # Deserialize best genome
        # Deserialize bp_assigned_mods
        bp_assigned_mods = dict()
        for spec, assigned_mod in saved_state['best_genome']['bp_assigned_modules'].items():
            bp_assigned_mods[int(spec)] = self._deserialize_module(assigned_mod, dtype, module_config_params)

        # Deserialize underlying blueprint of best genome
        best_genome_bp = self._deserialize_blueprint(saved_state['best_genome']['blueprint'])

        self.best_genome = CoDeepNEATGenome(genome_id=saved_state['best_genome']['genome_id'],
                                            blueprint=best_genome_bp,
                                            bp_assigned_modules=bp_assigned_mods,
                                            output_layers=saved_state['best_genome']['output_layers'],
                                            input_shape=tuple(saved_state['best_genome']['input_shape']),
                                            dtype=dtype,
                                            origin_generation=saved_state['best_genome']['origin_generation'])

    @staticmethod
    def _deserialize_module(mod_params, dtype, module_config_params) -> CoDeepNEATModuleBase:
        """"""
        mod_type = mod_params['module_type']
        del mod_params['module_type']
        return MODULES[mod_type](config_params=module_config_params[mod_type],
                                 dtype=dtype,
                                 **mod_params)

    @staticmethod
    def _deserialize_blueprint(bp_params) -> CoDeepNEATBlueprint:
        """"""
        # Deserialize Blueprint graph
        bp_graph = dict()
        for gene_id, gene_params in bp_params['blueprint_graph'].items():
            if 'node' in gene_params:
                bp_graph[int(gene_id)] = CoDeepNEATBlueprintNode(gene_id, gene_params['node'], gene_params['species'])
            else:
                bp_graph[int(gene_id)] = CoDeepNEATBlueprintConn(gene_id,
                                                                 gene_params['conn_start'],
                                                                 gene_params['conn_end'],
                                                                 gene_params['enabled'])
        # Recreate optimizer factory
        optimizer_factory = OptimizerFactory(bp_params['optimizer_factory'])

        # Recreate deserialized Blueprint
        return CoDeepNEATBlueprint(bp_params['blueprint_id'],
                                   bp_params['parent_mutation'],
                                   bp_graph,
                                   optimizer_factory)
