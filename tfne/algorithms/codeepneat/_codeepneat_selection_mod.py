import math
from typing import Union


class CoDeepNEATSelectionMOD:
    def _select_modules_basic(self) -> ({Union[int, str]: int}, {int: int}, {int}):
        """"""
        raise NotImplementedError()

        '''
        mod_spec_parents = dict()
        for spec_id, spec_mod_ids in self.pop.mod_species.items():
            # Sort module ids in species according to their fitness
            spec_mod_ids_sorted = sorted(spec_mod_ids, key=lambda x: self.pop.modules[x].get_fitness())

            spec_elites = set(spec_mod_ids_sorted[-self.mod_spec_mod_elitism:])
            spec_elites.add(self.pop.mod_species_repr[spec_id])

            reprod_threshold_index = math.ceil(len(spec_mod_ids) * self.mod_spec_reprod_thres)
            spec_parents = set(spec_mod_ids_sorted[reprod_threshold_index:])
            spec_parents = spec_parents.union(spec_elites)

            mod_ids_non_elite = set(spec_mod_ids) - spec_elites
            mod_ids_non_parental = set(spec_mod_ids) - spec_parents
            for mod_id in mod_ids_non_elite:
                self.pop.mod_species[spec_id].remove(mod_id)
            for mod_id in mod_ids_non_parental:
                del self.pop.modules[mod_id]

            mod_spec_parents[spec_id] = spec_parents

        ################################################################################################################

        # Determine the sum of all average fitness
        total_avg_fitness = 0
        for fitness_history in self.pop.mod_species_fitness_history.values():
            total_avg_fitness += fitness_history[self.pop.generation_counter]

        mod_spec_ordered = sorted(self.pop.mod_species.keys(),
                                  key=lambda x: self.pop.mod_species_fitness_history[x][self.pop.generation_counter])

        mod_spec_offspring = dict()
        available_mod_pop = self.mod_pop_size
        for spec_id in mod_spec_ordered:
            spec_fitness = self.pop.mod_species_fitness_history[spec_id][self.pop.generation_counter]
            spec_fitness_share = spec_fitness / total_avg_fitness
            spec_intended_size = round(spec_fitness_share * available_mod_pop)

            if len(self.pop.mod_species[spec_id]) + self.mod_spec_min_offspring > spec_intended_size:
                mod_spec_offspring[spec_id] = self.mod_spec_min_offspring
                available_mod_pop -= len(self.pop.mod_species[spec_id]) + self.mod_spec_min_offspring
            else:
                mod_spec_offspring[spec_id] = spec_intended_size - len(self.pop.mod_species[spec_id])
                available_mod_pop -= spec_intended_size
            total_avg_fitness -= spec_fitness

        return mod_spec_offspring, mod_spec_parents, mod_spec_extinct
        '''

        '''
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
        for spec_id, spec_mod_ids in self.pop.mod_species.items():
            # Sort module ids in species according to their fitness
            spec_mod_ids_sorted = sorted(spec_mod_ids, key=lambda x: self.pop.modules[x].get_fitness(), reverse=True)

            # Determine module ids to remove in order to prevent to use them for reproduction
            removal_threshold_index = int(len(spec_mod_ids) * (1 - self.mod_spec_reprod_thres))
            # Correct removal index threshold if reproduction threshold so high that elitism modules would be removed
            if removal_threshold_index + self.mod_spec_mod_elitism < len(spec_mod_ids):
                removal_threshold_index = self.mod_spec_mod_elitism
            spec_mod_ids_to_remove = spec_mod_ids_sorted[removal_threshold_index:]

            # Delete low performing modules that will not be considered for reproduction from species assignment
            for mod_id_to_remove in spec_mod_ids_to_remove:
                self.pop.mod_species[spec_id].remove(mod_id_to_remove)
                del self.pop.modules[mod_id_to_remove]

        # Set reinit offspring to 0 and extinct_species to an empty list as no species can go extinct in basic selection
        reinit_offspring = 0
        extinct_species = []
        return mod_species_offspring, reinit_offspring, extinct_species
        '''

    def _select_modules_param_distance_fixed(self) -> ({Union[int, str]: int}, {int: int}, {int}):
        """"""
        ### Species Extinction ###
        # Determine if species can be considered for extinction. Critera: Species existed long enough; species can be
        # removed according to species elitism; species is not the last of its module type. Then determine if species is
        # stagnating for the recent config specified time period (meaning that it had not improved at any time in the
        # recent time period).
        # Preprocess current species by listing the frequency of module types as to not remove the last species of a
        # unique module type.
        spec_type_frequency = dict()
        for mod_id in self.pop.mod_species_repr.values():
            spec_mod_type = self.pop.modules[mod_id].get_module_type()
            if spec_mod_type in spec_type_frequency:
                spec_type_frequency[spec_mod_type] += 1
            else:
                spec_type_frequency[spec_mod_type] = 1

        # Order species according to their fitness in order to remove low performing species first
        mod_species_ordered = sorted(self.pop.mod_species.keys(),
                                     key=lambda x: self.pop.mod_species_fitness_history[x][self.pop.generation_counter])

        # Traverse ordered species list. Keep track of extinct species and the total fitness achieved by those extinct
        # species as relevant for later calculation of reinitialized offspring, if option activated.
        extinct_fitness = 0
        mod_spec_extinct = set()
        for spec_id in mod_species_ordered:
            # Don't consider species for extinction if it hasn't existed long enough
            if len(self.pop.mod_species_fitness_history[spec_id]) < self.mod_spec_max_stagnation + 1:
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
                # Species is stagnating. Flag species as extinct, keep track of its fitness and then remove it from the
                # population
                mod_spec_extinct.add(spec_id)
                extinct_fitness += self.pop.mod_species_fitness_history[spec_id][self.pop.generation_counter]
                spec_type_frequency[spec_mod_type] -= 1
                for mod_id in self.pop.mod_species[spec_id]:
                    del self.pop.modules[mod_id]
                del self.pop.mod_species[spec_id]
                del self.pop.mod_species_repr[spec_id]
                del self.pop.mod_species_fitness_history[spec_id]

        ### Generational Parent Determination ###
        # Determine potential parents of the module species for offspring creation. Modules are ordered by their fitness
        # and the top x percent of those modules (as dictated via the reproduction threshold parameter) are chosen as
        # generational parents. The species elite modules (best members and representative) are added as potential
        # parents, even if the representative does not make the cut according to the reproduction threshold.
        mod_spec_parents = dict()
        for spec_id, spec_mod_ids in self.pop.mod_species.items():
            # Sort module ids in species according to their fitness
            spec_mod_ids_sorted = sorted(spec_mod_ids, key=lambda x: self.pop.modules[x].get_fitness())

            # Determine the species elite as the top x members and the species representative
            spec_elites = set(spec_mod_ids_sorted[-self.mod_spec_mod_elitism:])
            spec_elites.add(self.pop.mod_species_repr[spec_id])

            # Determine the species parents as those clearing the reproduction threshold, plus the species elites
            reprod_threshold_index = math.ceil(len(spec_mod_ids) * self.mod_spec_reprod_thres)
            spec_parents = set(spec_mod_ids_sorted[reprod_threshold_index:])
            spec_parents = spec_parents.union(spec_elites)

            # Remove non elite modules from the species list, as they are not part of the species anymore. Remove non
            # parental modules from the module container as there is no use of those modules anymore.
            mod_ids_non_elite = set(spec_mod_ids) - spec_elites
            mod_ids_non_parental = set(spec_mod_ids) - spec_parents
            for mod_id in mod_ids_non_elite:
                self.pop.mod_species[spec_id].remove(mod_id)
            for mod_id in mod_ids_non_parental:
                del self.pop.modules[mod_id]

            # Cast potential parents to tuple, as randomly chosen from
            mod_spec_parents[spec_id] = tuple(spec_parents)

        #### Offspring Size Calculation ####
        # Determine the amount of offspring for each species as well as the amount of reinitialized modules, in case
        # this option is activated. Each species is assigned offspring according to its species share of the total
        # fitness, though minimum offspring constraints are considered. Preprocess by determining the sum of all
        # average fitness and removing the extinct species from the species order
        total_avg_fitness = 0
        for fitness_history in self.pop.mod_species_fitness_history.values():
            total_avg_fitness += fitness_history[self.pop.generation_counter]
        for spec_id in mod_spec_extinct:
            mod_species_ordered.remove(spec_id)

        # Determine the amount of offspring to be reinitialized as the fitness share of the total fitness by the extinct
        # species
        mod_spec_offspring = dict()
        available_mod_pop = self.mod_pop_size
        if self.mod_spec_reinit_extinct and extinct_fitness > 0:
            extinct_fitness_share = extinct_fitness / (total_avg_fitness + extinct_fitness)
            reinit_offspring = int(extinct_fitness_share * available_mod_pop)
            mod_spec_offspring['reinit'] = reinit_offspring
            available_mod_pop -= reinit_offspring

        # Work through each species in order (from least to most fit) and determine the intended size as the species
        # fitness share of the total fitness of the remaining species, applied to the remaining population slots.
        # Assign offspring under the consideration of the minimal offspring constraint and then decrease the total
        # fitness and the remaining population slots.
        for spec_id in mod_species_ordered:
            spec_fitness = self.pop.mod_species_fitness_history[spec_id][self.pop.generation_counter]
            spec_fitness_share = spec_fitness / total_avg_fitness
            spec_intended_size = round(spec_fitness_share * available_mod_pop)

            if len(self.pop.mod_species[spec_id]) + self.mod_spec_min_offspring > spec_intended_size:
                mod_spec_offspring[spec_id] = self.mod_spec_min_offspring
                available_mod_pop -= len(self.pop.mod_species[spec_id]) + self.mod_spec_min_offspring
            else:
                mod_spec_offspring[spec_id] = spec_intended_size - len(self.pop.mod_species[spec_id])
                available_mod_pop -= spec_intended_size
            total_avg_fitness -= spec_fitness

        # Return
        # mod_spec_offspring {int: int} associating species id with amount of offspring
        # mod_spec_parents {int: [int]} associating species id with list of potential parent ids for species
        # mod_spec_extinct {int} listing all modules species that went extinct in this generation
        return mod_spec_offspring, mod_spec_parents, mod_spec_extinct

    def _select_modules_param_distance_dynamic(self) -> ({Union[int, str]: int}, {int: int}, {int}):
        """"""
        # selection process identical for both variants of module speciation
        return self._select_modules_param_distance_fixed()
