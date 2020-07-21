import math


class CoDeepNEATSelectionBP:
    def _select_blueprints_basic(self) -> ({int: int}, int):
        """"""
        #### Offspring Size Calculation ####
        # Determine the sum of each avg fitness
        total_avg_fitness = 0
        for fitness_history in self.pop.bp_species_fitness_history.values():
            total_avg_fitness += fitness_history[self.pop.generation_counter]

        # Calculate the amount of offspring assigned to each species based on the species share of the total avg fitness
        bp_species_offspring = dict()
        current_total_size = 0
        for spec_id, spec_fitness_history in self.pop.bp_species_fitness_history.items():
            # The intended future size of the species is its share of the total avg fitness
            spec_fitness_share = spec_fitness_history[self.pop.generation_counter] / total_avg_fitness
            spec_intended_size = math.floor(spec_fitness_share * self.bp_pop_size)

            # Determine the assigned offspring size of the species, which is its determined size minus the blueprints
            # which will be preserved
            offspring_size = spec_intended_size - self.bp_spec_bp_elitism
            if offspring_size <= self.bp_spec_min_offspring:
                offspring_size = self.bp_spec_min_offspring

            bp_species_offspring[spec_id] = offspring_size
            current_total_size += (offspring_size + self.bp_spec_bp_elitism)

        # If during math flooring operations and minimal offspring calculations the total size of the future species
        # deviates from the intended bp size, adjust the offspring by removing offspring from the species with the
        # most assigned offspring or adding offspring by adding offspring to the species with least assigned offspring
        while current_total_size < self.bp_pop_size:
            min_spec_id = min(bp_species_offspring.keys(), key=bp_species_offspring.get)
            bp_species_offspring[min_spec_id] += 1
            current_total_size += 1
        while current_total_size > self.bp_pop_size:
            max_spec_id = max(bp_species_offspring.keys(), key=bp_species_offspring.get)
            bp_species_offspring[max_spec_id] -= 1
            current_total_size -= 1

        #### Blueprint Selection ####
        for spec_id, spec_bp_ids in self.pop.bp_species.items():
            # Sort blueprint ids in species according to their fitness
            spec_bp_ids_sorted = sorted(spec_bp_ids, key=lambda x: self.pop.blueprints[x].get_fitness(), reverse=True)

            # Determine blueprint ids to remove in order to prevent to use them for reproduction
            removal_threshold_index = int(len(spec_bp_ids) * (1 - self.bp_spec_reprod_thres))
            # Correct removal index threshold if reproduction threshold so high that elitism blueprints would be removed
            if removal_threshold_index + self.bp_spec_bp_elitism < len(spec_bp_ids):
                removal_threshold_index = self.bp_spec_bp_elitism
            spec_bp_ids_to_remove = spec_bp_ids_sorted[removal_threshold_index:]

            # Delete low performing blueprints that will not be considered for reproduction from species assignment
            for bp_id_to_remove in spec_bp_ids_to_remove:
                self.pop.bp_species[spec_id].remove(bp_id_to_remove)
                del self.pop.blueprints[bp_id_to_remove]

        # Set reinit offspring to 0 as no species can go extinct in basic selection
        reinit_offspring = 0
        return bp_species_offspring, reinit_offspring

    def _select_blueprints_gene_overlap_fixed(self) -> ({int: int}, int):
        """"""
        #### Determination of Species Extinction ####
        # Determine if species can be considered for extinction. Critera: Species existed long enough or species can be
        # removed according to species elitism. Then determine if species is stagnating for the recent config specified
        # time period (meaning that it had not improved at any time in the recent time period). First create order in
        # which to consider species for extinction in order to remove low performing species first. Consider species
        # with the currently lowest avg fitness first
        spec_select_order = sorted(self.pop.bp_species.keys(),
                                   key=lambda x: self.pop.bp_species_fitness_history[x][self.pop.generation_counter])
        bp_extinct_species = list()
        for spec_id in spec_select_order:
            # Don't consider species for extinction if it hasn't existed long enough
            if len(self.pop.bp_species_fitness_history[spec_id]) + 1 < self.bp_spec_max_stagnation:
                continue
            # Don't consider species for extinction if species elitism doesn't allow removal of further species
            if len(self.pop.bp_species) <= self.bp_spec_species_elitism:
                continue

            # Consider species for extinction and determine if it has been stagnating
            distant_generation = self.pop.generation_counter - self.bp_spec_max_stagnation
            distant_avg_fitness = self.pop.bp_species_fitness_history[spec_id][distant_generation]
            recent_fitness = list()
            for i in range(self.bp_spec_max_stagnation):
                recent_fitness.append(self.pop.bp_species_fitness_history[spec_id][self.pop.generation_counter - i])
            if distant_avg_fitness >= max(recent_fitness):
                # Species is stagnating. Flag species to be removed later.
                bp_extinct_species.append(spec_id)

        #### Offspring Size Calculation ####
        # Distinguish offspring size calculation depending on if extinct offspring will be reinitialized or not
        # (see config option 'bp_spec_reinit_extinct')
        reinit_offspring = 0
        bp_species_offspring = dict()
        if self.bp_spec_reinit_extinct and len(bp_extinct_species) > 0:
            # Determine total average fitness of all species, including the species going extinct
            total_avg_fitness = 0
            for fitness_history in self.pop.bp_species_fitness_history.values():
                total_avg_fitness += fitness_history[self.pop.generation_counter]

            # Determine the assigned offspring size of each species. The intended species size is the species share of
            # the total avg fitness, while the species offspring is this size minus the elite blueprints that will be
            # preserved. Population space that is intended for species that will be removed is instead allocated to the
            # reinit_offspring counter, which dictates how many new blueprints will be reinitialized during actual
            # blueprint evolution
            current_total_size = 0
            for spec_id, spec_fitness_history in self.pop.bp_species_fitness_history.items():
                # The intended future size of the species is its share of the total avg fitness
                spec_fitness_share = spec_fitness_history[self.pop.generation_counter] / total_avg_fitness
                spec_intended_size = math.floor(spec_fitness_share * self.bp_pop_size)

                if spec_id in bp_extinct_species:
                    # Allocate species size that is about to go extinct to reinit_offspring counter
                    reinit_offspring += spec_intended_size
                    current_total_size += spec_intended_size
                else:
                    # Determine offspring size and correct to minimal offspring size if needed
                    offspring_size = spec_intended_size - self.bp_spec_bp_elitism
                    if offspring_size <= self.bp_spec_min_offspring:
                        offspring_size = self.bp_spec_min_offspring

                    bp_species_offspring[spec_id] = offspring_size
                    current_total_size += (offspring_size + self.bp_spec_bp_elitism)

            # If during math flooring operations and minimal offspring calculations the total size of the future species
            # deviates from the intended blueprint population size, adjust the offspring by either removing/adding
            # offspring from/to the species or reinit_offspring size counter with the most/least members.
            while current_total_size < self.bp_pop_size:
                min_spec_id = min(bp_species_offspring.keys(), key=bp_species_offspring.get)
                if bp_species_offspring[min_spec_id] < reinit_offspring:
                    bp_species_offspring[min_spec_id] += 1
                    current_total_size += 1
                else:
                    reinit_offspring += 1
                    current_total_size += 1
            while current_total_size > self.bp_pop_size:
                max_spec_id = max(bp_species_offspring.keys(), key=bp_species_offspring.get)
                if bp_species_offspring[max_spec_id] > reinit_offspring:
                    bp_species_offspring[max_spec_id] -= 1
                    current_total_size -= 1
                else:
                    reinit_offspring -= 1
                    current_total_size -= 1

        else:  # No reinitialization of extinct species or no species going extinct
            # Determine total average fitness of all species, excluding the species going extinct
            total_avg_fitness = 0
            for spec_id, fitness_history in self.pop.bp_species_fitness_history.items():
                if spec_id not in bp_extinct_species:
                    total_avg_fitness += fitness_history[self.pop.generation_counter]

            # Calculate the amount of assigned offspring for each species for evolution. This is based on the species
            # share of the total avg fitness excluding the extinct species. The perservering species that won't go
            # extinct will occupy the population space previously held by those species going extinct.
            current_total_size = 0
            for spec_id, spec_fitness_history in self.pop.bp_species_fitness_history.items():
                # Disregard offspring calculation for species going extinct. Their fitness is not included in the total
                if spec_id in bp_extinct_species:
                    continue

                # Determine offspring size and correct to minimal offspring size if needed
                spec_fitness_share = spec_fitness_history[self.pop.generation_counter] / total_avg_fitness
                spec_intended_size = math.floor(spec_fitness_share * self.bp_pop_size)
                offspring_size = spec_intended_size - self.bp_spec_bp_elitism
                if offspring_size <= self.bp_spec_min_offspring:
                    offspring_size = self.bp_spec_min_offspring

                bp_species_offspring[spec_id] = offspring_size
                current_total_size += (offspring_size + self.bp_spec_bp_elitism)

            # If during math flooring operations and minimal offspring calculations the total size of the future species
            # deviates from the intended blueprint size, adjust the offspring by removing offspring from the species
            # with the most assigned offspring or adding offspring by adding offspring to the species with least
            # assigned offspring
            while current_total_size < self.bp_pop_size:
                min_spec_id = min(bp_species_offspring.keys(), key=bp_species_offspring.get)
                bp_species_offspring[min_spec_id] += 1
                current_total_size += 1
            while current_total_size > self.bp_pop_size:
                max_spec_id = max(bp_species_offspring.keys(), key=bp_species_offspring.get)
                bp_species_offspring[max_spec_id] -= 1
                current_total_size -= 1

        #### Blueprint Selection ####
        # Remove the species and their elements that were determined to go extinct.
        for spec_id in bp_extinct_species:
            for bp_id in self.pop.bp_species[spec_id]:
                del self.pop.blueprints[bp_id]
            del self.pop.bp_species[spec_id]
            del self.pop.bp_species_repr[spec_id]
            del self.pop.bp_species_fitness_history[spec_id]

        # If all species went extinct, return as evolution will abort
        if len(self.pop.bp_species) == 0:
            return None, None

        # Remove the elements from each surviving species that do not pass the reproduction threshold
        for spec_id, spec_bp_ids in self.pop.bp_species.items():
            # Sort blueprint ids in species according to their fitness
            spec_bp_ids_sorted = sorted(spec_bp_ids, key=lambda x: self.pop.blueprints[x].get_fitness(), reverse=True)

            # Determine blueprint ids to remove in order to prevent to use them for reproduction
            removal_threshold_index = int(len(spec_bp_ids) * (1 - self.bp_spec_reprod_thres))
            # Correct removal index threshold if reproduction threshold so high that elitism blueprints would be removed
            if removal_threshold_index + self.bp_spec_bp_elitism < len(spec_bp_ids):
                removal_threshold_index = self.bp_spec_bp_elitism
            spec_bp_ids_to_remove = spec_bp_ids_sorted[removal_threshold_index:]

            # Exclude the species representative from removal, in case the species representative does not clear the
            # removal threshold of the species
            spec_bp_ids_to_remove = [bp_id for bp_id in spec_bp_ids_to_remove
                                     if bp_id != self.pop.bp_species_repr[spec_id]]

            # Delete low performing blueprints that will not be considered for reproduction from species assignment
            for bp_id_to_remove in spec_bp_ids_to_remove:
                self.pop.bp_species[spec_id].remove(bp_id_to_remove)
                del self.pop.blueprints[bp_id_to_remove]

        # Return the determined blueprint species offspring dict and the count of reinitialized offspring
        return bp_species_offspring, reinit_offspring

    def _select_blueprints_gene_overlap_dynamic(self) -> ({int: int}, int):
        """"""
        # selection process identical for both variants of blueprint speciation
        return self._select_blueprints_gene_overlap_fixed()
