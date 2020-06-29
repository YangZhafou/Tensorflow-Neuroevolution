class CoDeepNEATSpeciationBP:
    def _speciate_blueprints_basic(self, new_blueprint_ids):
        """"""
        ### Removal of parental but not elite Blueprints ###
        # Remove blueprints that will not be carried over from blueprint container after evolution, though which were
        # kept as potential parent. First sort blueprint ids in species according to their fitness
        bp_ids_sorted = sorted(self.bp_species[1], key=lambda x: self.blueprints[x].get_fitness(), reverse=True)

        # Determine blueprint ids that were kept but are not carried over
        bp_ids_to_carry_over = bp_ids_sorted[:self.bp_spec_bp_elitism]
        bp_ids_to_remove = [bp_id for bp_id in self.bp_species[1] if bp_id not in bp_ids_to_carry_over]

        # Delete just determined blueprint ids from blueprint container and blueprint species list
        for bp_id_to_remove in bp_ids_to_remove:
            self.bp_species[1].remove(bp_id_to_remove)
            del self.blueprints[bp_id_to_remove]

        ### Species Assignment ###
        # Basic speciation assigns each new blueprint to species 1, as the only existing species
        self.bp_species[1] += new_blueprint_ids
