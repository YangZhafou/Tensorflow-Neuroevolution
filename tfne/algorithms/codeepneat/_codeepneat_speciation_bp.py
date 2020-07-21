import statistics


class CoDeepNEATSpeciationBP:
    def _speciate_blueprints_basic(self, new_blueprint_ids):
        """"""
        ### Removal of parental but not elite Blueprints ###
        # Remove blueprints that will not be carried over from blueprint container after evolution, though which were
        # kept as potential parent. First sort blueprint ids in species according to their fitness
        bp_ids_sorted = sorted(self.pop.bp_species[1], key=lambda x: self.pop.blueprints[x].get_fitness(), reverse=True)

        # Determine blueprint ids that were kept but are not carried over
        bp_ids_to_carry_over = bp_ids_sorted[:self.bp_spec_bp_elitism]
        bp_ids_to_remove = [bp_id for bp_id in self.pop.bp_species[1] if bp_id not in bp_ids_to_carry_over]

        # Delete just determined blueprint ids from blueprint container and blueprint species list
        for bp_id_to_remove in bp_ids_to_remove:
            self.pop.bp_species[1].remove(bp_id_to_remove)
            del self.pop.blueprints[bp_id_to_remove]

        ### Species Assignment ###
        # Basic speciation assigns each new blueprint to species 1, as the only existing species
        self.pop.bp_species[1] += new_blueprint_ids

    def _speciate_blueprints_gene_overlap_fixed(self, new_blueprint_ids):
        """"""
        ### Removal of parental but not elite Blueprints ###
        # Remove blueprints that will not be carried over due to blueprint elitism from blueprint container after
        # evolution, though which were kept as potential parents
        for spec_id, spec_bp_ids in self.pop.bp_species.items():
            # Sort blueprint ids in species according to their fitness
            spec_bp_ids_sorted = sorted(spec_bp_ids,
                                        key=lambda x: self.pop.blueprints[x].get_fitness(),
                                        reverse=True)

            # As the current species representative has to always be carried over to the next species for the purpose
            # of assigning new blueprint to the according species, check if species representative is among the elite
            # blueprints. If not then decrease blueprint elitism by 1 and also carry over the species representative
            if self.pop.bp_species_repr[spec_id] in spec_bp_ids_sorted[:self.bp_spec_bp_elitism]:
                spec_bp_ids_to_carry_over = spec_bp_ids_sorted[:self.bp_spec_bp_elitism]
                spec_bp_ids_to_remove = [bp_id for bp_id in spec_bp_ids if
                                         bp_id not in spec_bp_ids_to_carry_over]
            else:
                spec_bp_ids_to_carry_over = spec_bp_ids_sorted[:(self.bp_spec_bp_elitism - 1)]
                spec_bp_ids_to_remove = [bp_id for bp_id in spec_bp_ids if
                                         bp_id not in spec_bp_ids_to_carry_over and
                                         bp_id != self.pop.bp_species_repr[spec_id]]

            # Delete just determined blueprint ids from the blueprint species list and the blueprint container
            for bp_id_to_remove in spec_bp_ids_to_remove:
                self.pop.bp_species[spec_id].remove(bp_id_to_remove)
                del self.pop.blueprints[bp_id_to_remove]

        ### Species Assignment ###
        # Traverse all new blueprint ids and compare their parameter distance with other species. If the distance to one
        # species is below the config specified 'bp_spec_distance' then assign the new blueprint to that species. If
        # not, create a new species
        for bp_id in new_blueprint_ids:
            # Calculate the distance of the blueprint to each species representative and associate each species with its
            # distance in the blueprint_spec_distances dict
            blueprint_spec_distances = dict()
            for spec_id, spec_bp_repr_id in self.pop.bp_species_repr.items():
                spec_bp_repr = self.pop.blueprints[self.pop.bp_species_repr[spec_id]]
                blueprint_spec_distances[spec_id] = spec_bp_repr.calculate_gene_overlap(self.pop.blueprints[bp_id])

            # Determine if of all the distances to other species on distance falls below the config specified
            # 'bp_spec_distance', signaling that the blueprint should be assigned to this species
            min_bp_spec_distance = min(blueprint_spec_distances.values())
            if min_bp_spec_distance <= self.bp_spec_distance:
                # Find the species to which the new blueprint has the minimal distance, which is sufficiently small, and
                # assign the new blueprint to that species
                for spec_id, bp_spec_distance in blueprint_spec_distances.items():
                    if bp_spec_distance == min_bp_spec_distance:
                        self.pop.bp_species[spec_id].append(bp_id)
            else:
                # Create a new species with the new blueprint as the representative
                self.pop.bp_species_counter += 1
                self.pop.bp_species[self.pop.bp_species_counter] = [bp_id]
                self.pop.bp_species_repr[self.pop.bp_species_counter] = bp_id

        ### Rebase Species Representative ###
        # If Rebase representative config flag set to true, rechoose the representative of each species as the best
        # blueprint of the species that also holds the minimum set distance ('bp_spec_distance') to all other species
        # representatives
        if self.bp_spec_rebase_repr:
            for spec_id, spec_bp_repr_id in self.pop.bp_species_repr.items():
                # Determine the blueprint ids of all other species representatives and create a sorted list of the
                # blueprints in the current species according to their fitness
                other_spec_bp_repr_ids = [bp_id for bp_id in self.pop.bp_species_repr.values()
                                          if bp_id != spec_bp_repr_id]

                # Only consider members of the species that have been evaluated before as potential new species
                # representatives
                evaluated_bp_species = [bp_id for bp_id in self.pop.bp_species[spec_id]
                                        if self.pop.blueprints[bp_id].get_fitness() != 0]
                spec_bp_ids_sorted = sorted(evaluated_bp_species,
                                            key=lambda x: self.pop.blueprints[x].get_fitness(),
                                            reverse=True)

                # Traverse each blueprint id in the sorted blueprint id list beginning with the best. Determine the
                # distance to other species representative blueprint ids and if the distance to all other species
                # representatives is higher than the specified minimum distance for a new species, set the blueprint as
                # the new representative.
                for bp_id in spec_bp_ids_sorted:
                    if bp_id == spec_bp_repr_id:
                        # Best species blueprint already representative. Abort search
                        break
                    blueprint = self.pop.blueprints[bp_id]
                    distance_to_other_spec_repr = [blueprint.calculate_gene_overlap(self.pop.blueprints[other_bp_id])
                                                   for other_bp_id in other_spec_bp_repr_ids]
                    if all(distance >= self.bp_spec_distance for distance in distance_to_other_spec_repr):
                        # New best species representative found. Set as representative and abort search
                        self.pop.bp_species_repr[spec_id] = bp_id
                        break

    def _speciate_blueprints_gene_overlap_dynamic(self, new_blueprint_ids):
        """"""
        # Perform gene-overlap-fixed speciation as identical to dynamic variant and subsequently adjust distance
        self._speciate_blueprints_gene_overlap_fixed(new_blueprint_ids)

        ### Dynamic Adjustment of Species Distance ###
        # If the species count is too low, decrease the species distance by 10 percent. If the species count is too
        # high, determine the distances of each species representative to all other species representatives and choose
        # the distance that would set the species count right. Average that optimal distance for each species repr out
        # to get the new species distance.
        if len(self.pop.bp_species) < self.bp_spec_species_count:
            self.bp_spec_distance = self.bp_spec_distance * 0.9
        elif len(self.pop.bp_species) > self.bp_spec_species_count:
            optimal_spec_distance_per_species = list()
            for spec_id, spec_bp_repr_id in self.pop.bp_species_repr.items():
                bp_repr = self.pop.blueprints[spec_bp_repr_id]
                # Determine distance of species repr to all other species repr
                other_spec_bp_repr_ids = [bp_id for bp_id in self.pop.bp_species_repr.values()
                                          if bp_id != spec_bp_repr_id]
                distances_to_other_specs = [bp_repr.calculate_gene_overlap(self.pop.blueprints[other_bp_id])
                                            for other_bp_id in other_spec_bp_repr_ids]
                sorted_distances_to_other_specs = sorted(distances_to_other_specs)
                # Set optimal distance of current species repr such that it conforms to 'bp_spec_species_count'
                optimal_spec_distance = sorted_distances_to_other_specs[-self.bp_spec_species_count - 1]
                optimal_spec_distance_per_species.append(optimal_spec_distance)

            # Average out all optimal distances for each species repr to get the new distance
            self.bp_spec_distance = statistics.mean(optimal_spec_distance_per_species)
