import math
import statistics


class CoDeepNEATSelectionMOD:
    def _select_modules_basic(self) -> ({int: int}, int, bool):
        """"""
        #### Offspring Size Calculation ####
        # Determine average fitness of each current species as well as the sum of each avg fitness
        mod_species_avg_fitness = dict()
        for spec_id, spec_mod_ids in self.mod_species.items():
            spec_avg_fitness = statistics.mean([self.modules[mod_id].get_fitness() for mod_id in spec_mod_ids])
            mod_species_avg_fitness[spec_id] = spec_avg_fitness
        total_avg_fitness = sum(mod_species_avg_fitness.values())

        # Calculate the amount of offspring assigned to each species based on the species share of the total avg fitness
        mod_species_offspring = dict()
        current_total_size = 0
        for spec_id, spec_avg_fitness in mod_species_avg_fitness.items():
            spec_size = math.floor((spec_avg_fitness / total_avg_fitness) * self.mod_pop_size)

            # Determine the assigned offspring size of the species, which is its determined size minus the modules
            # which will be preserved
            offspring_size = spec_size - self.mod_spec_mod_elitism
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
        # Determine average fitness of each current species and append it to the species avg fitness history
        for spec_id, spec_mod_ids in self.mod_species.items():
            spec_avg_fitness = statistics.mean([self.modules[mod_id].get_fitness() for mod_id in spec_mod_ids])
            if spec_id in self.mod_species_fitness_history:
                self.mod_species_fitness_history[spec_id].append(spec_avg_fitness)
            else:
                self.mod_species_fitness_history[spec_id] = [spec_avg_fitness]

        # Determine if species has existed long enough to be considered for extinction. Then determine if it stagnated
        # for the recent config specified time period (meaning that it had not produced a better fitness in the recent
        # time period than before)
        spec_ids_to_remove = list()
        for spec_id in self.mod_species:
            if len(self.mod_species_fitness_history[spec_id]) >= self.mod_spec_max_stagnation:
                distant_avg_fitness = self.mod_species_fitness_history[spec_id][-self.mod_spec_max_stagnation]
                recent_fitness_history = self.mod_species_fitness_history[spec_id][-self.mod_spec_max_stagnation:]
                if distant_avg_fitness >= max(recent_fitness_history):
                    spec_ids_to_remove.append(spec_id)

        # Remove just determined species and species elements
        for spec_id in spec_ids_to_remove:
            for mod_id in self.mod_species[spec_id]:
                del self.modules[mod_id]
            del self.mod_species[spec_id]
            del self.mod_species_repr[spec_id]
            del self.mod_species_fitness_history[spec_id]

        print("FORCED EXIT")
        exit()

    def _select_modules_param_distance_dynamic(self) -> ({int: int}, int, bool):
        """"""
        # selection process identical for both variants of module speciation
        return self._select_modules_param_distance_fixed()
