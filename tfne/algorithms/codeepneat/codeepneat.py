import sys
import json
import random
import statistics

from absl import logging

import tfne
from ..base_algorithm import BaseNeuroevolutionAlgorithm
from ...encodings.codeepneat import CoDeepNEATGenome

from ._codeepneat_config_processing import CoDeepNEATConfigProcessing
from ._codeepneat_initialization import CoDeepNEATInitialization
from ._codeepneat_selection_mod import CoDeepNEATSelectionMOD
from ._codeepneat_selection_bp import CoDeepNEATSelectionBP
from ._codeepneat_evolution_mod import CoDeepNEATEvolutionMOD
from ._codeepneat_evolution_bp import CoDeepNEATEvolutionBP
from ._codeepneat_speciation_mod import CoDeepNEATSpeciationMOD
from ._codeepneat_speciation_bp import CoDeepNEATSpeciationBP


class CoDeepNEAT(BaseNeuroevolutionAlgorithm,
                 CoDeepNEATConfigProcessing,
                 CoDeepNEATInitialization,
                 CoDeepNEATSelectionMOD,
                 CoDeepNEATSelectionBP,
                 CoDeepNEATEvolutionMOD,
                 CoDeepNEATEvolutionBP,
                 CoDeepNEATSpeciationMOD,
                 CoDeepNEATSpeciationBP):
    """"""

    def __init__(self, config, environment, initial_population_file_path=None):
        """"""
        # Register and process the supplied config and register the optionally supplied initial population
        self.config = config
        self._process_config()
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
        self.mod_species_counter = 0

        # Declare and initialize internal variables concerning the blueprint population of the CoDeepNEAT algorithm
        self.blueprints = dict()
        self.bp_species = dict()
        self.bp_species_repr = dict()
        self.bp_species_counter = 0

    def initialize_environments(self, num_cpus, num_gpus, verbosity):
        """"""
        # Initialize only one instance as implementation currently only supports single instance evaluation
        for _ in range(1):
            initialized_env = self.environment(weight_training=True, verbosity=verbosity, config=self.config)
            self.envs.append(initialized_env)

        # Determine required input and output dimensions and shape
        self.input_shape = self.envs[0].get_input_shape()
        self.input_dim = len(self.input_shape)
        self.output_shape = self.envs[0].get_output_shape()
        self.output_dim = len(self.output_shape)

    def initialize_population(self):
        """"""
        if self.initial_population_file_path is None:
            print("Initializing a new population of {} blueprints and {} modules..."
                  .format(self.bp_pop_size, self.mod_pop_size))

            # Set internal variables of the population to the initialization of a new population
            self.generation_counter = 0
            self.best_fitness = 0

            #### Initialize Module Population ####
            # Initialize module population with a basic speciation scheme, even when another speciation type is supplied
            # as config, only speciating modules according to their module type. Each module species (and therefore
            # module type) is initiated with the same amount of modules (or close to the same amount if module pop size
            # not evenly divisble). Parameters of all initial modules chosen as per module initialization implementation

            # Set initial species counter of basic speciation and initialize module species list
            self.mod_species_counter = len(self.available_modules)
            for i in range(self.mod_species_counter):
                spec_id = i + 1  # Start species counter with 1
                self.mod_species[spec_id] = list()

            for i in range(self.mod_pop_size):
                # Decide on for which species a new module is added (uniformly distributed)
                chosen_species = (i % self.mod_species_counter)

                # Determine type and the associated config parameters of chosen species and initialize a module with it
                mod_type = self.available_modules[chosen_species]
                mod_config_params = self.available_mod_params[mod_type]
                module_id, module = self.encoding.create_initial_module(mod_type=mod_type,
                                                                        config_params=mod_config_params)

                # Append newly created initial module to module container and to according species
                chosen_species_id = chosen_species + 1
                self.modules[module_id] = module
                self.mod_species[chosen_species_id].append(module_id)

                # Create a species representative if speciation method is not 'basic' and no representative chosen yet
                if self.mod_spec_type != 'basic' and chosen_species_id not in self.mod_species_repr:
                    self.mod_species_repr[chosen_species_id] = module_id

            #### Initialize Blueprint Population ####
            # Initialize blueprint population with a minimal blueprint graph, only consisting of an input node (with
            # None species or the 'input' species respectively) and a single output node, having a randomly assigned
            # species. All hyperparameters of the blueprint are uniform randomly chosen. All blueprints are not
            # speciated in the beginning and are assigned to species 1.

            # Initialize blueprint species list and create tuple of the possible species the output node can take on
            self.bp_species[1] = list()
            available_mod_species = tuple(self.mod_species.keys())

            for _ in range(self.bp_pop_size):
                # Determine the module species of the initial (and only) node
                initial_node_species = random.choice(available_mod_species)

                # Initialize a new blueprint with minimal graph only using initial node species
                blueprint_id, blueprint = self._create_initial_blueprint(initial_node_species)

                # Append newly create blueprint to blueprint container and to only initial blueprint species
                self.blueprints[blueprint_id] = blueprint
                self.bp_species[1].append(blueprint_id)

                # Create a species representative if speciation method is not 'basic' and no representative chosen yet
                if self.bp_spec_type != 'basic' and 1 not in self.bp_species_repr:
                    self.bp_species_repr[1] = blueprint_id
        else:
            raise NotImplementedError("Initializing population with pre-evolved initial population not yet implemented")

    def evaluate_population(self) -> (int, int):
        """"""
        # Create container collecting the fitness of the genomes that involve specific modules. Calculate the average
        # fitness of the genomes in which a module is involved in later and assign it as the module's fitness
        mod_fitnesses_in_genomes = dict()

        # Initialize Progress counter variables for evaluate population progress bar. Print notice of evaluation start
        genome_pop_size = self.bp_pop_size * self.genomes_per_bp
        genome_eval_counter = 0
        genome_eval_counter_div = round(genome_pop_size / 40.0, 4)
        print("\nEvaluating {} genomes in generation {}...".format(genome_pop_size, self.generation_counter))
        print_str = "\r[{:40}] {}/{} Genomes".format("", genome_eval_counter, genome_pop_size)
        sys.stdout.write(print_str)
        sys.stdout.flush()

        # Evaluate each blueprint independent from its species by building 'genomes_per_bp' genomes and averaging out
        # and assigning the resulting fitness
        for blueprint in self.blueprints.values():
            # Get the species ids of all species present in the blueprint currently evaluated
            bp_module_species = blueprint.get_species()

            # Create container collecting the fitness of the genomes that involve that specific blueprint.
            bp_fitnesses_in_genomes = list()

            for _ in range(self.genomes_per_bp):
                # Assemble genome by first uniform randomly choosing a specific module from the species that the
                # blueprint nodes are referring to.
                bp_assigned_modules = dict()
                for i in bp_module_species:
                    chosen_module_id = random.choice(self.mod_species[i])
                    bp_assigned_modules[i] = self.modules[chosen_module_id]

                try:
                    # Create genome, using the specific blueprint, a dict of modules for each species, the configured
                    # output layers and input shape as well as the current generation
                    genome_id, genome = self.encoding.create_genome(blueprint,
                                                                    bp_assigned_modules,
                                                                    self.output_layers,
                                                                    self.input_shape,
                                                                    self.generation_counter)

                except ValueError:
                    # Catching build value error, occuring when the supplied layers and parameters do not result in a
                    # valid TF model. See warning string.
                    bp_id = blueprint.get_id()
                    mod_spec_to_id = dict()
                    for spec, mod in bp_assigned_modules.items():
                        mod_spec_to_id[spec] = mod.get_id()
                    logging.warning(f"CoDeepNEAT tried combining the Blueprint ID {bp_id} with the module assignment "
                                    f"{mod_spec_to_id}, resulting in an invalid neural network model. Setting genome "
                                    f"fitness to 0.")

                    # Setting genome id and genome to None as referenced later. Setting genome fitness to 0 to
                    # discourage continued use of the blueprint and modules resulting in this faulty model.
                    genome_id, genome = None, None
                    genome_fitness = 0

                else:
                    # Now evaluate genome on registered environment and set its fitness
                    # NOTE: As CoDeepNEAT implementation currently only supports 1 eval instance, automatically choose
                    # that instance from the environment list
                    genome_fitness = self.envs[0].eval_genome_fitness(genome)
                    genome.set_fitness(genome_fitness)

                # Print population evaluation progress bar
                genome_eval_counter += 1
                progress_mult = int(round(genome_eval_counter / genome_eval_counter_div, 4))
                print_str = "\r[{:40}] {}/{} Genomes | Genome ID {} achieved fitness of {}".format("=" * progress_mult,
                                                                                                   genome_eval_counter,
                                                                                                   genome_pop_size,
                                                                                                   genome_id,
                                                                                                   genome_fitness)
                sys.stdout.write(print_str)
                sys.stdout.flush()

                # Assign the genome fitness to the blueprint and all modules used for the creation of the genome
                bp_fitnesses_in_genomes.append(genome_fitness)
                for assigned_module in bp_assigned_modules.values():
                    module_id = assigned_module.get_id()
                    if module_id in mod_fitnesses_in_genomes:
                        mod_fitnesses_in_genomes[module_id].append(genome_fitness)
                    else:
                        mod_fitnesses_in_genomes[module_id] = [genome_fitness]

                # Register genome as new best if it exhibits better fitness than the previous best
                if self.best_fitness is None or genome_fitness > self.best_fitness:
                    self.best_genome = genome
                    self.best_fitness = genome_fitness

            # Average out collected fitness of genomes the blueprint was invovled in. Then assign that average fitness
            # to the blueprint
            bp_fitnesses_in_genomes_avg = round(statistics.mean(bp_fitnesses_in_genomes), 4)
            blueprint.set_fitness(bp_fitnesses_in_genomes_avg)

        # Average out collected fitness of genomes each module was invovled in. Then assign that average fitness to the
        # module
        for mod_id, mod_fitness_list in mod_fitnesses_in_genomes.items():
            mod_genome_fitness_avg = round(statistics.mean(mod_fitness_list), 4)
            self.modules[mod_id].set_fitness(mod_genome_fitness_avg)

        return self.generation_counter, self.best_fitness

    def summarize_population(self):
        """"""
        # Calculate average fitnesses of each module species and total module pop. Determine best module of each species
        mod_species_avg_fitness = dict()
        mod_species_best_id = dict()
        for spec_id, spec_mod_ids in self.mod_species.items():
            spec_total_fitness = 0
            for mod_id in spec_mod_ids:
                mod_fitness = self.modules[mod_id].get_fitness()
                spec_total_fitness += mod_fitness
                if spec_id not in mod_species_best_id or mod_fitness > mod_species_best_id[spec_id][1]:
                    mod_species_best_id[spec_id] = (mod_id, mod_fitness)
            mod_species_avg_fitness[spec_id] = round(spec_total_fitness / len(spec_mod_ids), 4)
        modules_avg_fitness = round(sum(mod_species_avg_fitness.values()) / len(mod_species_avg_fitness), 4)

        # Calculate average fitnesses of each bp species and total bp pop. Determine best bp of each species
        bp_species_avg_fitness = dict()
        bp_species_best_id = dict()
        for spec_id, spec_bp_ids in self.bp_species.items():
            spec_total_fitness = 0
            for bp_id in spec_bp_ids:
                bp_fitness = self.blueprints[bp_id].get_fitness()
                spec_total_fitness += bp_fitness
                if spec_id not in bp_species_best_id or bp_fitness > bp_species_best_id[spec_id][1]:
                    bp_species_best_id[spec_id] = (bp_id, bp_fitness)
            bp_species_avg_fitness[spec_id] = round(spec_total_fitness / len(spec_bp_ids), 4)
        blueprints_avg_fitness = round(sum(bp_species_avg_fitness.values()) / len(bp_species_avg_fitness), 4)

        # Print summary header
        print("\n\n\n\033[1m{}  Population Summary  {}\n\n"
              "Generation: {:>4}  ||  Best Genome Fitness: {:>8}  ||  Average Blueprint Fitness: {:>8}  ||  "
              "Average Module Fitness: {:>8}\033[0m\n"
              "Best Genome: {}\n".format('#' * 60,
                                         '#' * 60,
                                         self.generation_counter,
                                         self.best_fitness,
                                         blueprints_avg_fitness,
                                         modules_avg_fitness,
                                         self.best_genome))

        # Print summary of blueprint species
        print("\033[1mBP Species                || BP Species Avg Fitness                || BP Species Size\n"
              "Best BP of Species\033[0m")
        for spec_id, spec_bp_avg_fitness in bp_species_avg_fitness.items():
            print("{:>6}                    || {:>8}                              || {:>8}\n{}"
                  .format(spec_id,
                          spec_bp_avg_fitness,
                          len(self.bp_species[spec_id]),
                          self.blueprints[bp_species_best_id[spec_id][0]]))

        # Print summary of module species
        print("\n\033[1mModule Species            || Module Species Avg Fitness            || "
              "Module Species Size\nBest Module of Species\033[0m")
        for spec_id, spec_mod_avg_fitness in mod_species_avg_fitness.items():
            print("{:>6}                    || {:>8}                              || {:>8}\n{}"
                  .format(spec_id,
                          spec_mod_avg_fitness,
                          len(self.mod_species[spec_id]),
                          self.modules[mod_species_best_id[spec_id][0]]))

        # Print summary footer
        print("\n\033[1m" + '#' * 142 + "\033[0m\n")

    def evolve_population(self) -> bool:
        """"""

        #### Select Modules ####
        if self.mod_spec_type == 'basic':
            mod_species_offspring, mod_reinit_offspring, pop_extinct = self._select_modules_basic()
        elif self.mod_spec_type == 'param-distance-fixed':
            mod_species_offspring, mod_reinit_offspring, pop_extinct = self._select_modules_param_distance_fixed()
        elif self.mod_spec_type == 'param-distance-dynamic':
            mod_species_offspring, mod_reinit_offspring, pop_extinct = self._select_modules_param_distance_dynamic()
        else:
            raise RuntimeError(f"Module speciation type '{self.mod_spec_type}' not yet implemented")

        # If population went extinct abort evolution and return True
        if pop_extinct:
            return True

        #### Select Blueprints ####
        if self.bp_spec_type == 'basic':
            bp_species_offspring, bp_reinit_offspring, pop_extinct = self._select_blueprints_basic()
        elif self.bp_spec_type == 'gene-overlap-fixed':
            bp_species_offspring, bp_reinit_offspring, pop_extinct = self._select_blueprints_gene_overlap_fixed()
        elif self.bp_spec_type == 'gene-overlap-dynamic':
            bp_species_offspring, bp_reinit_offspring, pop_extinct = self._select_blueprints_gene_overlap_dynamic()
        else:
            raise RuntimeError(f"Blueprint speciation type '{self.bp_spec_type}' not yet implemented")

        # If population went extinct abort evolution and return True
        if pop_extinct:
            return True

        #### Evolve Modules ####
        new_module_ids = self._evolve_modules(mod_species_offspring, mod_reinit_offspring)

        #### Evolve Blueprints ####
        new_blueprint_ids = self._evolve_blueprints(bp_species_offspring, bp_reinit_offspring)

        #### Speciate Modules ####
        if self.mod_spec_type == 'basic':
            self._speciate_modules_basic(new_module_ids)
        elif self.mod_spec_type == 'param-distance-fixed':
            self._speciate_modules_param_distance_fixed(new_module_ids)
        elif self.mod_spec_type == 'param-distance-dynamic':
            self._speciate_modules_param_distance_dynamic(new_module_ids)
        else:
            raise RuntimeError(f"Module speciation type '{self.mod_spec_type}' not yet implemented")

        #### Speciate Blueprints ####
        if self.bp_spec_type == 'basic':
            self._speciate_blueprints_basic(new_blueprint_ids)
        elif self.bp_spec_type == 'gene-overlap-fixed':
            self._speciate_blueprints_gene_overlap_fixed(new_blueprint_ids)
        elif self.bp_spec_type == 'gene-overlap-dynamic':
            self._speciate_blueprints_gene_overlap_dynamic(new_blueprint_ids)
        else:
            raise RuntimeError(f"Blueprint speciation type '{self.bp_spec_type}' not yet implemented")

        #### Return ####
        # Adjust generation counter and return False, signalling that the population has not gone extinct
        self.generation_counter += 1
        return False

    def save_population(self, save_dir_path):
        """"""
        # Set save file name as 'pop backup' and including the current generation
        if save_dir_path[-1] != '/':
            save_dir_path += '/'
        save_file_path = save_dir_path + f"tfne_run_backup_gen_{self.generation_counter}.json"

        # Serialize all modules for json output
        serialized_modules = dict()
        for mod_id, module in self.modules.items():
            serialized_modules[mod_id] = module.serialize()

        # Serialize all blueprints for json output
        serialized_blueprints = dict()
        for bp_id, blueprint in self.blueprints.items():
            serialized_blueprints[bp_id] = blueprint.serialize()

        # Use serialized module and blueprint population and extend it by algorithm internal evolution information
        serialized_population = {
            'generation_counter': self.generation_counter,
            'modules': serialized_modules,
            'mod_species': self.mod_species,
            'mod_species_repr': self.mod_species_repr if self.mod_species_repr else None,
            'mod_species_counter': self.mod_species_counter,
            'blueprints': serialized_blueprints,
            'bp_species': self.bp_species,
            'bp_species_repr': self.bp_species_repr if self.bp_species_repr else None,
            'bp_species_counter': self.bp_species_counter,
            'best_genome': self.best_genome.serialize()
        }

        # Save the just serialzied population as a json file
        with open(save_file_path, 'w') as save_file:
            json.dump(serialized_population, save_file, indent=4)
        print(f"Backed up generation {self.generation_counter} of the CoDeepNEAT run to file: {save_file_path}")

    def get_best_genome(self) -> CoDeepNEATGenome:
        """"""
        return self.best_genome
