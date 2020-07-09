import math
import statistics


class CoDeepNEATSelectionBP:
    def _select_blueprints_basic(self) -> ({int: int}, int, bool):
        """"""
        #### Offspring Size Calculation ####
        # Determine average fitness of each current species as well as the sum of each avg fitness
        bp_species_avg_fitness = dict()
        for spec_id, spec_bp_ids in self.bp_species.items():
            spec_avg_fitness = statistics.mean([self.blueprints[bp_id].get_fitness() for bp_id in spec_bp_ids])
            bp_species_avg_fitness[spec_id] = spec_avg_fitness
        total_avg_fitness = sum(bp_species_avg_fitness.values())

        # Calculate the amount of offspring assigned to each species based on the species share of the total avg fitness
        bp_species_offspring = dict()
        current_total_size = 0
        for spec_id, spec_avg_fitness in bp_species_avg_fitness.items():
            spec_size = math.floor((spec_avg_fitness / total_avg_fitness) * self.bp_pop_size)

            # Determine the assigned offspring size of the species, which is its determined size minus the blueprints
            # which will be preserved
            offspring_size = spec_size - self.bp_spec_bp_elitism
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
        for spec_id, spec_bp_ids in self.bp_species.items():
            # Sort blueprint ids in species according to their fitness
            spec_bp_ids_sorted = sorted(spec_bp_ids, key=lambda x: self.blueprints[x].get_fitness(), reverse=True)

            # Determine blueprint ids to remove in order to prevent to use them for reproduction
            removal_threshold_index = int(len(spec_bp_ids) * (1 - self.bp_spec_reprod_thres))
            # Correct removal index threshold if reproduction threshold so high that elitism blueprints would be removed
            if removal_threshold_index + self.bp_spec_bp_elitism < len(spec_bp_ids):
                removal_threshold_index = self.bp_spec_bp_elitism
            spec_bp_ids_to_remove = spec_bp_ids_sorted[removal_threshold_index:]

            # Delete low performing blueprints that will not be considered for reproduction from species assignment
            for bp_id_to_remove in spec_bp_ids_to_remove:
                self.bp_species[spec_id].remove(bp_id_to_remove)
                del self.blueprints[bp_id_to_remove]

        # Set reinit offspring to 0 and extinction to False, as no species can go extinct in basic selection
        reinit_offspring = 0
        pop_extinction = False
        return bp_species_offspring, reinit_offspring, pop_extinction


    def _select_blueprints_gene_overlap_fixed(self) -> ({int: int}, int, bool):
        """"""
        print("FORCED EXIT")
        exit()

    def _select_blueprints_gene_overlap_dynamic(self) -> ({int: int}, int, bool):
        """"""
        # selection process identical for both variants of blueprint speciation
        return self._select_blueprints_gene_overlap_fixed()
