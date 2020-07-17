import math


class CoDeepNEATSelectionMOD:
    def _select_modules_basic(self) -> ({int: int}, int, bool):
        """"""
        #### Offspring Size Calculation ####
        # Determine the sum of each avg fitness
        total_avg_fitness = 0
        for fitness_history in self.pop.mod_species_fitness_history.values():
            total_avg_fitness += fitness_history[self.pop.generation_counter]

        # Calculate the amount of offspring assigned to each species based on the species share of the total avg fitness
        mod_species_offspring = dict()
        current_total_size = 0
        for spec_id, spec_fitness_history in self.pop.mod_species_fitness_history.items():
            # The intended future size of the species is its share of the total avg fitness
            spec_fitness_share = spec_fitness_history[self.pop.generation_counter] / total_avg_fitness
            spec_intended_size = math.floor(spec_fitness_share * self.mod_pop_size)

            # Determine the assigned offspring size of the species, which is its determined size minus the modules
            # which will be preserved
            offspring_size = spec_intended_size - self.mod_spec_mod_elitism
            if offspring_size <= self.mod_spec_min_offspring:
                offspring_size = self.mod_spec_min_offspring

            mod_species_offspring[spec_id] = offspring_size
            current_total_size += (offspring_size + self.mod_spec_mod_elitism)

        # If during math flooring operations and minimal offspring calculations the total size of the future species
        # deviates from the intended module size, adjust the offspring by removing offspring from the species with the
        # most assigned offspring or adding offspring by adding offspring to the species with least assigned offspring
        while current_total_size < self.mod_pop_size:
            min_spec_id = min(mod_species_offspring.keys(), key=mod_species_offspring.get)
            mod_species_offspring[min_spec_id] += 1
            current_total_size += 1
        while current_total_size > self.mod_pop_size:
            max_spec_id = max(mod_species_offspring.keys(), key=mod_species_offspring.get)
            mod_species_offspring[max_spec_id] -= 1
            current_total_size -= 1

        #### Module Selection ####
        for spec_id, spec_mod_ids in self.mod_species.items():
            # Sort module ids in species according to their fitness
            spec_mod_ids_sorted = sorted(spec_mod_ids, key=lambda x: self.modules[x].get_fitness(), reverse=True)

            # Determine module ids to remove in order to prevent to use them for reproduction
            removal_threshold_index = int(len(spec_mod_ids) * (1 - self.mod_spec_reprod_thres))
            # Correct removal index threshold if reproduction threshold so high that elitism modules would be removed
            if removal_threshold_index + self.mod_spec_mod_elitism < len(spec_mod_ids):
                removal_threshold_index = self.mod_spec_mod_elitism
            spec_mod_ids_to_remove = spec_mod_ids_sorted[removal_threshold_index:]

            # Delete low performing modules that will not be considered for reproduction from species assignment
            for mod_id_to_remove in spec_mod_ids_to_remove:
                self.mod_species[spec_id].remove(mod_id_to_remove)
                del self.modules[mod_id_to_remove]

        # Set reinit offspring to 0 and extinction to False, as no species can go extinct in basic selection
        reinit_offspring = 0
        pop_extinction = False
        return mod_species_offspring, reinit_offspring, pop_extinction

    def _select_modules_param_distance_fixed(self) -> ({int: int}, int, bool):
        """"""
        #### Determination of Species Extinction ####
        # Determine if species can be considered for extinction. Critera: Species existed long enough; species can be
        # removed according to species elitism; species is not the last of its module type. Then determine if species is
        # stagnating for the recent config specified time period (meaning that it had not improved at any time in the
        # recent time period). Preprocess current species by listing the frequency of module types as to not remove the
        # last species of a unique module type
        spec_type_frequency = dict()
        for mod_id in self.pop.mod_species_repr.values():
            spec_mod_type = self.pop.modules[mod_id].get_module_type()
            if spec_mod_type in spec_type_frequency:
                spec_type_frequency[spec_mod_type] += 1
            else:
                spec_type_frequency[spec_mod_type] = 1

        # Create order in which to consider species for extinction in order to remove low performing species first.
        # Consider species with the currently lowest avg fitness first
        spec_select_order = sorted(self.pop.mod_species.keys(),
                                   key=lambda x: self.pop.mod_species_fitness_history[x][self.pop.generation_counter])

        # Determine species ids to remove according to the above stated criteria
        spec_ids_to_remove = list()
        for spec_id in spec_select_order:
            # Don't consider species for extinction if it hasn't existed long enough
            if len(self.pop.mod_species_fitness_history[spec_id]) < self.mod_spec_max_stagnation:
                continue
            # Don't consider species for extinction if species elitism doesn't allow removal of further species
            if len(self.pop.mod_species) <= self.mod_spec_species_elitism:
                continue
            # Don't consider species for extinction if it is the last of its module type and species elitism is set to
            # a value higher than all possible module types.
            spec_mod_type = self.pop.modules[self.pop.mod_species_repr[spec_id]].get_module_type()
            if spec_type_frequency[spec_mod_type] == 1 and self.mod_spec_species_elitism >= len(self.available_modules):
                continue

            # Consider species for extinction and determine if it has been stagnating by checking if the distant avg
            # fitness is higher than all recent avg fitnesses
            distant_generation = self.pop.generation_counter - self.mod_spec_max_stagnation
            distant_avg_fitness = self.pop.mod_species_fitness_history[spec_id][distant_generation]
            recent_fitness = list()
            for i in range(self.mod_spec_max_stagnation):
                recent_fitness.append(self.pop.mod_species_fitness_history[spec_id][self.pop.generation_counter - i])
            if distant_avg_fitness >= max(recent_fitness):
                # Species is stagnating. Flag species to be removed later and decrement species type frequency
                spec_ids_to_remove.append(spec_id)
                spec_type_frequency[species_mod_type] -= 1

        #### Offspring Size Calculation ####
        # Distinguish offspring size calculation depending on if extinct offspring will be reinitialized or not
        # (see config option 'mod_spec_reinit_extinct')
        reinit_offspring = 0
        mod_species_offspring = dict()
        if self.mod_spec_reinit_extinct and len(spec_ids_to_remove) > 0:
            # Determine total average fitness of all species, including the species going extinct
            total_avg_fitness = 0
            for fitness_history in self.pop.mod_species_fitness_history.values():
                total_avg_fitness += fitness_history[self.pop.generation_counter]

            # Determine the assigned offspring size of each species. The intended species size is the species share of
            # the total avg fitness, while the species offspring is this size minus the elite modules that will be
            # preserved. Population space that is intended for species that will be removed is instead allocated to the
            # reinit_offspring counter, which dictates how many new modules will be reinitialized during actual module
            # evolution
            current_total_size = 0
            for spec_id, spec_fitness_history in self.pop.mod_species_fitness_history.items():
                # The intended future size of the species is its share of the total avg fitness
                spec_fitness_share = spec_fitness_history[self.pop.generation_counter] / total_avg_fitness
                spec_intended_size = math.floor(spec_fitness_share * self.mod_pop_size)

                if spec_id in spec_ids_to_remove:
                    # Allocate species size that is about to go extinct to reinit_offspring counter
                    reinit_offspring += spec_intended_size
                    current_total_size += spec_intended_size
                else:
                    # Determine offspring size and correct to minimal offspring size if needed
                    offspring_size = spec_intended_size - self.mod_spec_mod_elitism
                    if offspring_size <= self.mod_spec_min_offspring:
                        offspring_size = self.mod_spec_min_offspring

                    mod_species_offspring[spec_id] = offspring_size
                    current_total_size += (offspring_size + self.mod_spec_mod_elitism)

            # If during math flooring operations and minimal offspring calculations the total size of the future species
            # deviates from the intended module population size, adjust the offspring by either removing/adding
            # offspring from/to the species or reinit_offspring size counter with the most/least members.
            while current_total_size < self.mod_pop_size:
                min_spec_id = min(mod_species_offspring.keys(), key=mod_species_offspring.get)
                if mod_species_offspring[min_spec_id] < reinit_offspring:
                    mod_species_offspring[min_spec_id] += 1
                    current_total_size += 1
                else:
                    reinit_offspring += 1
                    current_total_size += 1
            while current_total_size > self.mod_pop_size:
                max_spec_id = max(mod_species_offspring.keys(), key=mod_species_offspring.get)
                if mod_species_offspring[max_spec_id] > reinit_offspring:
                    mod_species_offspring[max_spec_id] -= 1
                    current_total_size -= 1
                else:
                    reinit_offspring -= 1
                    current_total_size -= 1

        else:  # No reinitialization of extinct species or no species going extinct
            # Determine total average fitness of all species, excluding the species going extinct
            total_avg_fitness = 0
            for spec_id, fitness_history in self.pop.mod_species_fitness_history.items():
                if spec_id not in spec_ids_to_remove:
                    total_avg_fitness += fitness_history[self.pop.generation_counter]

            # Calculate the amount of assigned offspring for each species for evolution. This is based on the species
            # share of the total avg fitness excluding the extinct species. The perservering species that won't go
            # extinct will occupy the population space previously held by those species going extinct.
            current_total_size = 0
            for spec_id, spec_fitness_history in self.pop.mod_species_fitness_history.items():
                # Disregard offspring calculation for species going extinct. Their fitness is not included in the total
                if spec_id in spec_ids_to_remove:
                    continue

                # Determine offspring size and correct to minimal offspring size if needed
                spec_fitness_share = spec_fitness_history[self.pop.generation_counter] / total_avg_fitness
                spec_intended_size = math.floor(spec_fitness_share * self.mod_pop_size)
                offspring_size = spec_intended_size - self.mod_spec_mod_elitism
                if offspring_size <= self.mod_spec_min_offspring:
                    offspring_size = self.mod_spec_min_offspring

                mod_species_offspring[spec_id] = offspring_size
                current_total_size += (offspring_size + self.mod_spec_mod_elitism)

            # If during math flooring operations and minimal offspring calculations the total size of the future species
            # deviates from the intended module size, adjust the offspring by removing offspring from the species with
            # the most assigned offspring or adding offspring by adding offspring to the species with least assigned
            # offspring
            while current_total_size < self.mod_pop_size:
                min_spec_id = min(mod_species_offspring.keys(), key=mod_species_offspring.get)
                mod_species_offspring[min_spec_id] += 1
                current_total_size += 1
            while current_total_size > self.mod_pop_size:
                max_spec_id = max(mod_species_offspring.keys(), key=mod_species_offspring.get)
                mod_species_offspring[max_spec_id] -= 1
                current_total_size -= 1

        #### Module Selection ####
        # Remove the species and their elements that were determined to go extinct.
        for spec_id in spec_ids_to_remove:
            for mod_id in self.mod_species[spec_id]:
                del self.modules[mod_id]
            del self.mod_species[spec_id]
            del self.mod_species_repr[spec_id]
            del self.mod_species_fitness_history[spec_id]

        # If all species went extinct, return positive for pop_extinct
        if len(self.mod_species) == 0:
            return None, None, True

        # Remove the elements from each surviving species that do not pass the reproduction threshold
        for spec_id, spec_mod_ids in self.mod_species.items():
            # Sort module ids in species according to their fitness
            spec_mod_ids_sorted = sorted(spec_mod_ids, key=lambda x: self.modules[x].get_fitness(), reverse=True)

            # Determine module ids to remove in order to prevent to use them for reproduction
            removal_threshold_index = int(len(spec_mod_ids) * (1 - self.mod_spec_reprod_thres))
            # Correct removal index threshold if reproduction threshold so high that elitism modules would be removed
            if removal_threshold_index + self.mod_spec_mod_elitism < len(spec_mod_ids):
                removal_threshold_index = self.mod_spec_mod_elitism
            spec_mod_ids_to_remove = spec_mod_ids_sorted[removal_threshold_index:]

            # Exclude the species representative from removal, in case the species representative does not clear the
            # removal threshold of the species
            spec_mod_ids_to_remove = [mod_id for mod_id in spec_mod_ids_to_remove
                                      if mod_id != self.mod_species_repr[spec_id]]

            # Delete low performing modules that will not be considered for reproduction from species assignment
            for mod_id_to_remove in spec_mod_ids_to_remove:
                self.mod_species[spec_id].remove(mod_id_to_remove)
                del self.modules[mod_id_to_remove]

        # Return the determined module species offspring dict, the count of reinitialized offspring and the flag
        # indicating that the population did not go extinct
        pop_extinction = False
        return mod_species_offspring, reinit_offspring, pop_extinction

    def _select_modules_param_distance_dynamic(self) -> ({int: int}, int, bool):
        """"""
        # selection process identical for both variants of module speciation
        return self._select_modules_param_distance_fixed()
