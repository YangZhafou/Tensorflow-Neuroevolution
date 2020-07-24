import statistics


class CoDeepNEATSpeciationMOD:
    def _speciate_modules_basic(self, mod_spec_parents, new_module_ids):
        """"""

    def _speciate_modules_param_distance_fixed(self, mod_spec_parents, new_module_ids):
        """"""
        print("FORCED EXIT")
        exit()


        for spec_id, spec_parents in mod_spec_parents:
            spec_elites = self.pop.mod_species[spec_id]
            for mod_id in spec_parents:
                if mod_id not in spec_elites:
                    del self.pop.modules[mod_id]

        species_type_to_id = dict()
        for spec_id, spec_mod_repr_id in self.pop.mod_species_repr.items():
            species_type = self.pop.modules[spec_mod_repr_id].get_module_type()
            if species_type in species_type_to_id:
                species_type_to_id[species_type].append(spec_id)
            else:
                species_type_to_id[species_type] = [spec_id]

        raise NotImplementedError("Add consideration of a maximum species count")

        for mod_id in new_module_ids:
            module_type = self.pop.modules[mod_id].get_module_type()

            # Calculate the distance of the module to each species representative and associate each species with its
            # distance in the module_spec_distances dict
            module_spec_distances = dict()
            for spec_mod_type, spec_ids in species_type_to_id.items():
                if module_type != spec_mod_type:
                    continue

                for spec_id in spec_ids:
                    spec_mod_repr = self.pop.modules[self.pop.mod_species_repr[spec_id]]
                    module_spec_distances[spec_id] = spec_mod_repr.get_distance(self.pop.modules[mod_id])

            min_distance_spec = min(module_spec_distances, key=module_spec_distances.get)
            if module_spec_distances[min_distance_spec] <= self.mod_spec_distance:
                self.pop.mod_species[min_distance_spec].append(mod_id)
            else:
                # Create a new species with the new module as the representative
                self.pop.mod_species_counter += 1
                self.pop.mod_species[self.pop.mod_species_counter] = [mod_id]
                self.pop.mod_species_repr[self.pop.mod_species_counter] = mod_id
                species_type_to_id[module_type].append(self.pop.mod_species_counter)

        ### Rebase Species Representative ###
        # If Rebase representative config flag set to true, rechoose the representative of each species as the best
        # module of the species that also holds the minimum set distance ('mod_spec_distance') to all other species
        # representatives
        if self.mod_spec_rebase_repr:
            for spec_id, spec_mod_repr_id in self.pop.mod_species_repr.items():
                # Determine the module ids of all other species representatives and create a sorted list of the modules
                # in the current species according to their fitness
                other_spec_mod_repr_ids = [mod_id for mod_id in self.pop.mod_species_repr.values()
                                           if mod_id != spec_mod_repr_id]

                # Only consider members of the species that have been evaluated before as potential new species
                # representatives
                evaluated_mod_species = [mod_id for mod_id in self.pop.mod_species[spec_id]
                                         if self.pop.modules[mod_id].get_fitness() != 0]
                spec_mod_ids_sorted = sorted(evaluated_mod_species,
                                             key=lambda x: self.pop.modules[x].get_fitness(),
                                             reverse=True)
                # Traverse each module id in the sorted module id list beginning with the best. Determine the distance
                # to other species representative module ids and if the distance to all other species representatives is
                # higher than the specified minimum distance for a new species, set the module as the new
                # representative.
                for mod_id in spec_mod_ids_sorted:
                    if mod_id == spec_mod_repr_id:
                        # Best species module already representative. Abort search
                        break
                    module = self.pop.modules[mod_id]
                    distance_to_other_spec_repr = [module.get_distance(self.pop.modules[other_mod_id])
                                                   for other_mod_id in other_spec_mod_repr_ids]
                    if all(distance >= self.mod_spec_distance for distance in distance_to_other_spec_repr):
                        # New best species representative found. Set as representative and abort search
                        self.pop.mod_species_repr[spec_id] = mod_id
                        break

    def _speciate_modules_param_distance_dynamic(self, mod_spec_parents, new_module_ids):
        """"""
        # Perform param-distance-fixed speciation as identical to dynamic variant and subsequently adjust distance
        self._speciate_modules_param_distance_fixed(mod_spec_parents, new_module_ids)

        ### Dynamic Adjustment of Species Distance ###
        # If the species count is too low, decrease the species distance by 10 percent. If the species count is too
        # high, determine the distances of each species representative to all other species representatives and choose
        # the distance that would set the species count right. Average that optimal distance for each species repr out
        # to get the new species distance.
        if len(self.pop.mod_species) < self.mod_spec_species_count:
            self.mod_spec_distance = self.mod_spec_distance * 0.95
        elif len(self.pop.mod_species) > self.mod_spec_species_count:
            optimal_spec_distance_per_species = list()
            for spec_id, spec_mod_repr_id in self.pop.mod_species_repr.items():
                mod_repr = self.pop.modules[spec_mod_repr_id]
                # Determine distance of species repr to all other species repr
                other_spec_mod_repr_ids = [mod_id for mod_id in self.pop.mod_species_repr.values()
                                           if mod_id != spec_mod_repr_id]
                sorted_distances_to_other_specs = sorted([mod_repr.get_distance(self.pop.modules[other_mod_id])
                                                          for other_mod_id in other_spec_mod_repr_ids])
                # Set optimal distance of current species repr such that it conforms to 'mod_spec_species_count'
                optimal_spec_distance = sorted_distances_to_other_specs[-self.mod_spec_species_count]
                optimal_spec_distance_per_species.append(optimal_spec_distance)

            # Average out all optimal distances for each species repr to get the new distance
            self.mod_spec_distance = statistics.mean(optimal_spec_distance_per_species)

    '''
    def _speciate_modules_basic(self, new_module_ids):
        """"""
        # Determine module type of each species before all members of the species are potentially removed
        species_type_to_id = dict()
        for spec_id, spec_mod_repr_id in self.pop.mod_species_repr.items():
            species_type = self.pop.modules[spec_mod_repr_id].get_module_type()
            species_type_to_id[species_type] = spec_id

        ### Removal of parental but not elite Modules ###
        # Remove modules that will not be carried over from module container after evolution, though which were kept as
        # potential parent
        for spec_id, spec_mod_ids in self.pop.mod_species.items():
            # Sort module ids in species according to their fitness
            spec_mod_ids_sorted = sorted(spec_mod_ids, key=lambda x: self.pop.modules[x].get_fitness(), reverse=True)

            # Determine module ids that were kept but are not carried over
            spec_mod_ids_to_carry_over = spec_mod_ids_sorted[:self.mod_spec_mod_elitism]
            spec_mod_ids_to_remove = [mod_id for mod_id in spec_mod_ids if mod_id not in spec_mod_ids_to_carry_over]

            # Delete just determined module ids from module container and module species list
            for mod_id_to_remove in spec_mod_ids_to_remove:
                self.pop.mod_species[spec_id].remove(mod_id_to_remove)
                del self.pop.modules[mod_id_to_remove]

        ### Species Assignment ###
        # Basic speciation assigns each new module to the species with the according module type, as for each module
        # type there is only one species
        for mod_id in new_module_ids:
            mod_type = self.pop.modules[mod_id].get_module_type()
            according_mod_spec_id = species_mod_type_to_id[mod_type]
            self.pop.mod_species[according_mod_spec_id].append(mod_id)

    def _speciate_modules_param_distance_fixed(self, new_module_ids):
        """"""
        # Determine the species ids for each module type currently present, as new modules can only join species of
        # their own type and can therefore only be compared with modules of their own type
        species_type_to_id = dict()
        for spec_id, spec_mod_repr_id in self.pop.mod_species_repr.items():
            species_type = self.pop.modules[spec_mod_repr_id].get_module_type()
            if species_type in species_type_to_id:
                species_type_to_id[species_type].append(spec_id)
            else:
                species_type_to_id[species_type] = [spec_id]

        ### Removal of parental but not elite Modules ###
        # Remove modules that will not be carried over due to module elitism from module container after evolution,
        # though which were kept as potential parents
        for spec_id, spec_mod_ids in self.pop.mod_species.items():
            # Sort module ids in species according to their fitness
            spec_mod_ids_sorted = sorted(spec_mod_ids,
                                         key=lambda x: self.pop.modules[x].get_fitness(),
                                         reverse=True)

            # As the current species representative has to always be carried over to the next species for the purpose
            # of assigning new modules to the according species, check if species representative is among the elite
            # modules. If not then decrease module elitism by 1 and also carry over the species representative
            if self.pop.mod_species_repr[spec_id] in spec_mod_ids_sorted[:self.mod_spec_mod_elitism]:
                spec_mod_ids_to_carry_over = spec_mod_ids_sorted[:self.mod_spec_mod_elitism]
                spec_mod_ids_to_remove = [mod_id for mod_id in spec_mod_ids if
                                          mod_id not in spec_mod_ids_to_carry_over]
            else:
                spec_mod_ids_to_carry_over = spec_mod_ids_sorted[:(self.mod_spec_mod_elitism - 1)]
                spec_mod_ids_to_remove = [mod_id for mod_id in spec_mod_ids if
                                          mod_id not in spec_mod_ids_to_carry_over and
                                          mod_id != self.pop.mod_species_repr[spec_id]]

            # Delete just determined module ids from the module species list and the module container
            for mod_id_to_remove in spec_mod_ids_to_remove:
                self.pop.mod_species[spec_id].remove(mod_id_to_remove)
                del self.pop.modules[mod_id_to_remove]

        ### Species Assignment ###
        # Traverse all new module ids, determine their type and compare their parameter distance with other species of
        # that type. If the distance to one species of the same type is below the config specified 'mod_spec_distance'
        # then assign the new module to that species. If not, create a new species
        for mod_id in new_module_ids:
            module_type = self.pop.modules[mod_id].get_module_type()

            # Calculate the distance of the module to each species representative and associate each species with its
            # distance in the module_spec_distances dict
            module_spec_distances = dict()
            for spec_mod_type, spec_ids in species_type_to_id.items():
                if module_type != spec_mod_type:
                    continue

                for spec_id in spec_ids:
                    spec_mod_repr = self.pop.modules[self.pop.mod_species_repr[spec_id]]
                    module_spec_distances[spec_id] = spec_mod_repr.get_distance(self.pop.modules[mod_id])

            # Determine if of all the distances to other species on distance falls below the config specified
            # 'mod_spec_distance', signaling that the module should be assigned to this species
            min_mod_spec_distance = min(module_spec_distances.values())
            if min_mod_spec_distance <= self.mod_spec_distance:
                # Find the species to which the new module has the minimal distance, which is sufficiently small, and
                # assign the new module to that species
                for spec_id, mod_spec_distance in module_spec_distances.items():
                    if mod_spec_distance == min_mod_spec_distance:
                        self.pop.mod_species[spec_id].append(mod_id)
            else:
                # Create a new species with the new module as the representative
                self.pop.mod_species_counter += 1
                self.pop.mod_species[self.pop.mod_species_counter] = [mod_id]
                self.pop.mod_species_repr[self.pop.mod_species_counter] = mod_id
                species_type_to_id[module_type].append(self.pop.mod_species_counter)

        ### Rebase Species Representative ###
        # If Rebase representative config flag set to true, rechoose the representative of each species as the best
        # module of the species that also holds the minimum set distance ('mod_spec_distance') to all other species
        # representatives
        if self.mod_spec_rebase_repr:
            for spec_id, spec_mod_repr_id in self.pop.mod_species_repr.items():
                # Determine the module ids of all other species representatives and create a sorted list of the modules
                # in the current species according to their fitness
                other_spec_mod_repr_ids = [mod_id for mod_id in self.pop.mod_species_repr.values()
                                           if mod_id != spec_mod_repr_id]

                # Only consider members of the species that have been evaluated before as potential new species
                # representatives
                evaluated_mod_species = [mod_id for mod_id in self.pop.mod_species[spec_id]
                                         if self.pop.modules[mod_id].get_fitness() != 0]
                spec_mod_ids_sorted = sorted(evaluated_mod_species,
                                             key=lambda x: self.pop.modules[x].get_fitness(),
                                             reverse=True)
                # Traverse each module id in the sorted module id list beginning with the best. Determine the distance
                # to other species representative module ids and if the distance to all other species representatives is
                # higher than the specified minimum distance for a new species, set the module as the new
                # representative.
                for mod_id in spec_mod_ids_sorted:
                    if mod_id == spec_mod_repr_id:
                        # Best species module already representative. Abort search
                        break
                    module = self.pop.modules[mod_id]
                    distance_to_other_spec_repr = [module.get_distance(self.pop.modules[other_mod_id])
                                                   for other_mod_id in other_spec_mod_repr_ids]
                    if all(distance >= self.mod_spec_distance for distance in distance_to_other_spec_repr):
                        # New best species representative found. Set as representative and abort search
                        self.pop.mod_species_repr[spec_id] = mod_id
                        break

    def _speciate_modules_param_distance_dynamic(self, new_module_ids):
        """"""
        # Perform param-distance-fixed speciation as identical to dynamic variant and subsequently adjust distance
        self._speciate_modules_param_distance_fixed(new_module_ids)

        ### Dynamic Adjustment of Species Distance ###
        # If the species count is too low, decrease the species distance by 10 percent. If the species count is too
        # high, determine the distances of each species representative to all other species representatives and choose
        # the distance that would set the species count right. Average that optimal distance for each species repr out
        # to get the new species distance.
        if len(self.pop.mod_species) < self.mod_spec_species_count:
            self.mod_spec_distance = self.mod_spec_distance * 0.9
        elif len(self.pop.mod_species) > self.mod_spec_species_count:
            optimal_spec_distance_per_species = list()
            for spec_id, spec_mod_repr_id in self.pop.mod_species_repr.items():
                mod_repr = self.pop.modules[spec_mod_repr_id]
                # Determine distance of species repr to all other species repr
                other_spec_mod_repr_ids = [mod_id for mod_id in self.pop.mod_species_repr.values()
                                           if mod_id != spec_mod_repr_id]
                sorted_distances_to_other_specs = sorted([mod_repr.get_distance(self.pop.modules[other_mod_id])
                                                          for other_mod_id in other_spec_mod_repr_ids])
                # Set optimal distance of current species repr such that it conforms to 'mod_spec_species_count'
                optimal_spec_distance = sorted_distances_to_other_specs[-self.mod_spec_species_count]
                optimal_spec_distance_per_species.append(optimal_spec_distance)

            # Average out all optimal distances for each species repr to get the new distance
            self.mod_spec_distance = statistics.mean(optimal_spec_distance_per_species)
    '''
