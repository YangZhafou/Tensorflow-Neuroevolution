import random


class CoDeepNEATEvolutionMOD:
    def evolve_modules(self, mod_species_offspring, reinit_offspring) -> list:
        """"""
        # Create container for new modules that will be speciated in a later function
        new_module_ids = list()

        #### Evolve Modules ####
        # Traverse through each species and create according amount of offspring as determined prior during selection
        for spec_id, species_offspring in mod_species_offspring.items():
            for _ in range(species_offspring):
                # Choose randomly between mutation or crossover of module
                if random.random() < self.mod_mutation_prob:
                    ## Create new module through mutation ##
                    # Get a new module ID from the encoding, randomly determine the maximum degree of mutation and the
                    # parent module from the non removed modules of the current species. Then let the internal mutation
                    # function create a new module
                    mod_offspring_id = self.encoding.get_next_module_id()
                    max_degree_of_mutation = random.uniform(1e-323, self.mod_max_mutation)
                    parent_module = self.modules[random.choice(self.mod_species[spec_id])]

                    new_mod_id, new_mod = parent_module.create_mutation(mod_offspring_id,
                                                                        max_degree_of_mutation)
                else:  # random.random() < self.mod_mutation_prob + self.mod_crossover_prob
                    ## Create new module through crossover ##
                    # Determine if species has at least 2 modules as required for crossover
                    if len(self.mod_species[spec_id]) >= 2:
                        # Determine the 2 parent modules used for crossover
                        parent_module_1_id, parent_module_2_id = random.sample(self.mod_species[spec_id], k=2)
                        parent_module_1 = self.modules[parent_module_1_id]
                        parent_module_2 = self.modules[parent_module_2_id]

                        # Get a new module ID from encoding, randomly determine the maximum degree of mutation
                        mod_offspring_id = self.encoding.get_next_module_id()
                        max_degree_of_mutation = random.uniform(1e-323, self.mod_max_mutation)

                        # Determine the fitter parent module and let its internal crossover function create offspring
                        if parent_module_1.get_fitness() >= parent_module_2.get_fitness():
                            new_mod_id, new_mod = parent_module_1.create_crossover(mod_offspring_id,
                                                                                   parent_module_2,
                                                                                   max_degree_of_mutation)
                        else:
                            new_mod_id, new_mod = parent_module_2.create_crossover(mod_offspring_id,
                                                                                   parent_module_1,
                                                                                   max_degree_of_mutation)

                    else:
                        # As species does not have enough modules for crossover, perform a mutation on the remaining
                        # module
                        mod_offspring_id = self.encoding.get_next_module_id()
                        max_degree_of_mutation = random.uniform(1e-323, self.mod_max_mutation)
                        parent_module = self.modules[random.choice(self.mod_species[spec_id])]

                        new_mod_id, new_mod = parent_module.create_mutation(mod_offspring_id,
                                                                            max_degree_of_mutation)

                # Add newly created module to the module container and to the list of modules that have to be speciated
                self.modules[new_mod_id] = new_mod
                new_module_ids.append(new_mod_id)

        #### Reinitialize Modules ####
        # Initialize predetermined number of new modules as species went extinct and reinitialization is activated
        available_modules_count = len(self.available_modules)

        for i in range(reinit_offspring):
            # Decide on for which species a new module is added (uniformly distributed)
            chosen_species = i % available_modules_count

            # Determine type and the associated config parameters of chosen species and initialize a module with it
            mod_type = self.available_modules[chosen_species]
            mod_config_params = self.available_mod_params[mod_type]
            new_mod_id, new_mod = self.encoding.create_initial_module(mod_type=mod_type,
                                                                      config_params=mod_config_params)

            # Add newly created module to the module container and to the list of modules that have to be speciated
            self.modules[new_mod_id] = new_mod
            new_module_ids.append(new_mod_id)

        # Return the list of new module ids for later speciation
        return new_module_ids
