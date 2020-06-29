import math
import random

from ...helper_functions import round_with_step
from ...encodings.codeepneat.codeepneat_blueprint import CoDeepNEATBlueprintNode, CoDeepNEATBlueprintConn


class CoDeepNEATEvolutionBP:
    def _evolve_blueprints(self, bp_species_offspring, bp_reinit_offspring) -> list:
        """"""
        # Create container for new blueprints that will be speciated in a later function
        new_blueprint_ids = list()

        #### Evolve Blueprints ####
        # Calculate the brackets for a random float to fall into in order to choose a specific evolutionary method
        bp_mutation_add_node_bracket = self.bp_mutation_add_conn_prob + self.bp_mutation_add_node_prob
        bp_mutation_rem_conn_bracket = bp_mutation_add_node_bracket + self.bp_mutation_rem_conn_prob
        bp_mutation_rem_node_bracket = bp_mutation_rem_conn_bracket + self.bp_mutation_rem_node_prob
        bp_mutation_node_spec_bracket = bp_mutation_rem_node_bracket + self.bp_mutation_node_spec_prob
        bp_mutation_optimizer_bracket = bp_mutation_node_spec_bracket + self.bp_mutation_optimizer_prob

        # Traverse through each species and create according amount of offspring as determined prior during selection
        for spec_id, species_offspring in bp_species_offspring.items():
            for _ in range(species_offspring):
                # Choose random float vaue determining specific evolutionary method to evolve the chosen blueprint
                random_choice = random.random()
                if random_choice < self.bp_mutation_add_conn_prob:
                    ## Create new blueprint by adding connection ##
                    # Randomly determine the parent blueprint from the current species and the degree of mutation.
                    parent_blueprint = self.blueprints[random.choice(self.bp_species[spec_id])]
                    max_degree_of_mutation = random.uniform(1e-323, self.bp_max_mutation)
                    new_bp_id, new_bp = self._create_mutated_blueprint_add_conn(parent_blueprint,
                                                                                max_degree_of_mutation)

                elif random_choice < bp_mutation_add_node_bracket:
                    ## Create new blueprint by adding node ##
                    # Randomly determine the parent blueprint from the current species and the degree of mutation.
                    parent_blueprint = self.blueprints[random.choice(self.bp_species[spec_id])]
                    max_degree_of_mutation = random.uniform(1e-323, self.bp_max_mutation)
                    new_bp_id, new_bp = self._create_mutated_blueprint_add_node(parent_blueprint,
                                                                                max_degree_of_mutation)

                elif random_choice < bp_mutation_rem_conn_bracket:
                    ## Create new blueprint by removing connection ##
                    # Randomly determine the parent blueprint from the current species and the degree of mutation.
                    parent_blueprint = self.blueprints[random.choice(self.bp_species[spec_id])]
                    max_degree_of_mutation = random.uniform(1e-323, self.bp_max_mutation)
                    new_bp_id, new_bp = self._create_mutated_blueprint_rem_conn(parent_blueprint,
                                                                                max_degree_of_mutation)

                elif random_choice < bp_mutation_rem_node_bracket:
                    ## Create new blueprint by removing node ##
                    # Randomly determine the parent blueprint from the current species and the degree of mutation.
                    parent_blueprint = self.blueprints[random.choice(self.bp_species[spec_id])]
                    max_degree_of_mutation = random.uniform(1e-323, self.bp_max_mutation)
                    new_bp_id, new_bp = self._create_mutated_blueprint_rem_node(parent_blueprint,
                                                                                max_degree_of_mutation)

                elif random_choice < bp_mutation_node_spec_bracket:
                    ## Create new blueprint by mutating species in nodes ##
                    # Randomly determine the parent blueprint from the current species and the degree of mutation.
                    parent_blueprint = self.blueprints[random.choice(self.bp_species[spec_id])]
                    max_degree_of_mutation = random.uniform(1e-323, self.bp_max_mutation)
                    new_bp_id, new_bp = self._create_mutated_blueprint_node_spec(parent_blueprint,
                                                                                 max_degree_of_mutation)

                elif random_choice < bp_mutation_optimizer_bracket:
                    ## Create new blueprint by mutating the associated optimizer ##
                    # Randomly determine the parent blueprint from the current species.
                    parent_blueprint = self.blueprints[random.choice(self.bp_species[spec_id])]
                    new_bp_id, new_bp = self._create_mutated_blueprint_optimizer(parent_blueprint)

                else:  # random_choice < bp_crossover_bracket:
                    ## Create new blueprint through crossover ##
                    # Determine if species has at least 2 blueprints as required for crossover
                    if len(self.bp_species[spec_id]) >= 2:
                        # Randomly determine both parents for the blueprint crossover
                        parent_bp_1_id, parent_bp_2_id = random.sample(self.bp_species[spec_id], k=2)
                        parent_bp_1 = self.blueprints[parent_bp_1_id]
                        parent_bp_2 = self.blueprints[parent_bp_2_id]
                        new_bp_id, new_bp = self._create_crossed_over_blueprint(parent_bp_1,
                                                                                parent_bp_2)

                    else:
                        # As species does not have enough blueprints for crossover, perform a simple species
                        # perturbation in the blueprint nodes. Determine uniform randomly the parent blueprint from the
                        # current species and the degree of mutation.
                        parent_blueprint = self.blueprints[random.choice(self.bp_species[spec_id])]
                        max_degree_of_mutation = random.uniform(1e-323, self.bp_max_mutation)
                        new_bp_id, new_bp = self._create_mutated_blueprint_node_spec(parent_blueprint,
                                                                                     max_degree_of_mutation)

                # Add newly created blueprint to the bp container and to the list of bps that have to be speciated
                self.blueprints[new_bp_id] = new_bp
                new_blueprint_ids.append(new_bp_id)

        #### Reinitialize Blueprints ####
        # Initialize predetermined number of new blueprints as species went extinct and reinitialization is activated
        available_mod_species = tuple(self.mod_species.keys())

        for _ in range(bp_reinit_offspring):
            # Determine the module species of the initial (and only) node
            initial_node_species = random.choice(available_mod_species)

            # Initialize a new blueprint with minimal graph only using initial node species
            new_bp_id, new_bp = self._create_initial_blueprint(initial_node_species)

            # Add newly created blueprint to the bp container and to the list of bps that have to be speciated
            self.blueprints[new_bp_id] = new_bp
            new_blueprint_ids.append(new_bp_id)

        # Return the list of new blueprint ids for later speciation
        return new_blueprint_ids

    def _create_mutated_blueprint_add_conn(self, parent_blueprint, max_degree_of_mutation):
        """"""
        # Copy the parameters of the parent blueprint and get the pre-analyzed topology of the parent graph
        blueprint_graph, optimizer_factory = parent_blueprint.copy_parameters()
        bp_graph_topology = parent_blueprint.get_graph_topology()

        # Create the dict that keeps track of the way a blueprint has been mutated
        parent_mutation = {'parent_id': parent_blueprint.get_id(),
                           'mutation': 'add_conn',
                           'added_genes': list()}

        # Create collections of all nodes and present connections in the copied blueprint graph
        bp_graph_conns = set()
        bp_graph_nodes = list()
        for gene in blueprint_graph.values():
            if isinstance(gene, CoDeepNEATBlueprintNode):
                bp_graph_nodes.append(gene.node)
            elif gene.enabled:  # and isinstance(gene, CoDeepNEATBlueprintConn)
                # Only consider a connection for bp_graph_conns if it is enabled
                bp_graph_conns.add((gene.conn_start, gene.conn_end))

        # Remove end-node (node 2) from this list and shuffle it, as it later serves to randomly pop the start node of
        # the newly created connection
        bp_graph_nodes.remove(2)
        random.shuffle(bp_graph_nodes)

        # Determine specifically how many connections will be added
        number_of_conns_to_add = math.ceil(max_degree_of_mutation * len(bp_graph_conns))

        # Add connections in a loop until predetermined number of connections that are to be added is reached or until
        # the possible starting nodes run out
        added_conns_counter = 0
        while added_conns_counter < number_of_conns_to_add and len(bp_graph_nodes) > 0:
            # Choose random start node from all possible nodes by popping it from a preshuffled list of graph nodes
            start_node = bp_graph_nodes.pop()

            # Determine the list of all possible end nodes that are behind the start node as implementation currently
            # only supports feedforward topologies. Then shuffle the end nodes as they will later be randomly popped
            start_node_level = None
            for i in range(len(bp_graph_topology)):
                if start_node in bp_graph_topology[i]:
                    start_node_level = i
                    break
            possible_end_nodes = list(set().union(*bp_graph_topology[start_node_level + 1:]))
            random.shuffle(possible_end_nodes)

            # Traverse all possible end nodes randomly and create and add a blueprint connection to the offspring
            # blueprint graph if the specific connection tuple is not yet present.
            while len(possible_end_nodes) > 0:
                end_node = possible_end_nodes.pop()
                if (start_node, end_node) not in bp_graph_conns:
                    gene_id, gene = self.encoding.create_blueprint_conn(conn_start=start_node,
                                                                        conn_end=end_node)
                    blueprint_graph[gene_id] = gene
                    parent_mutation['added_genes'].append(gene_id)
                    added_conns_counter += 1

        # Create and return the offspring blueprint with the edited blueprint graph having additional connections as
        # well as the parent duplicated optimizer factory.
        return self.encoding.create_blueprint(blueprint_graph=blueprint_graph,
                                              optimizer_factory=optimizer_factory,
                                              parent_mutation=parent_mutation)

    def _create_mutated_blueprint_add_node(self, parent_blueprint, max_degree_of_mutation):
        """"""
        # Copy the parameters of the parent blueprint for the offspring
        blueprint_graph, optimizer_factory = parent_blueprint.copy_parameters()

        # Create the dict that keeps track of the way a blueprint has been mutated
        parent_mutation = {'parent_id': parent_blueprint.get_id(),
                           'mutation': 'add_node',
                           'added_genes': list()}

        # Analyze amount of nodes already present in bp graph as well as collect all gene ids of the present connections
        # that can possibly be split
        node_count = 0
        bp_graph_conn_ids = list()
        for gene in blueprint_graph.values():
            if isinstance(gene, CoDeepNEATBlueprintNode):
                node_count += 1
            elif gene.enabled:  # and isinstance(gene, CoDeepNEATBlueprintConn)
                # Only consider a connection for bp_graph_conn_ids if it is enabled
                bp_graph_conn_ids.append(gene.gene_id)

        # Determine how many nodes will be added, which connection gene_ids will be split for that and what possible
        # species can be assigned to those new nodes
        number_of_nodes_to_add = math.ceil(max_degree_of_mutation * node_count)
        gene_ids_to_split = random.sample(bp_graph_conn_ids, k=number_of_nodes_to_add)
        available_mod_species = tuple(self.mod_species.keys())

        # Split all chosen connections by setting them to disabled, querying the new node id from the encoding and then
        # creating the new node and the associated 2 connections through the encoding.
        for gene_id_to_split in gene_ids_to_split:
            # Determine start and end node of connection and disable it
            conn_start = blueprint_graph[gene_id_to_split].conn_start
            conn_end = blueprint_graph[gene_id_to_split].conn_end
            blueprint_graph[gene_id_to_split].set_enabled(False)

            # Create a new unique node if connection has not yet been split by any other mutation. Otherwise create the
            # same node. Choose species for new node randomly.
            new_node = self.encoding.get_node_for_split(conn_start, conn_end)
            new_species = random.choice(available_mod_species)

            # Create the node and connections genes for the new node addition and add them to the blueprint graph
            gene_id, gene = self.encoding.create_blueprint_node(node=new_node, species=new_species)
            blueprint_graph[gene_id] = gene
            parent_mutation['added_genes'].append(gene_id)
            gene_id, gene = self.encoding.create_blueprint_conn(conn_start=conn_start, conn_end=new_node)
            blueprint_graph[gene_id] = gene
            parent_mutation['added_genes'].append(gene_id)
            gene_id, gene = self.encoding.create_blueprint_conn(conn_start=new_node, conn_end=conn_end)
            blueprint_graph[gene_id] = gene
            parent_mutation['added_genes'].append(gene_id)

        # Create and return the offspring blueprint with the edited blueprint graph having a new node through a split
        # connection as well as the parent duplicated optimizer factory.
        return self.encoding.create_blueprint(blueprint_graph=blueprint_graph,
                                              optimizer_factory=optimizer_factory,
                                              parent_mutation=parent_mutation)

    def _create_mutated_blueprint_rem_conn(self, parent_blueprint, max_degree_of_mutation):
        """"""
        # Copy the parameters of the parent blueprint for the offspring
        blueprint_graph, optimizer_factory = parent_blueprint.copy_parameters()

        # Create the dict that keeps track of the way a blueprint has been mutated
        parent_mutation = {'parent_id': parent_blueprint.get_id(),
                           'mutation': 'rem_conn',
                           'removed_genes': list()}

        # Analyze amount of connections already present in bp graph and collect all gene ids whose connection ends in
        # certain nodes, allowing the algorithm to determine which connections can be removed as they are not the sole
        # connection to a remaining node.
        conn_count = 0
        bp_graph_incoming_conn_ids = dict()
        for gene in blueprint_graph.values():
            if isinstance(gene, CoDeepNEATBlueprintConn) and gene.enabled:
                conn_count += 1
                if gene.conn_end in bp_graph_incoming_conn_ids:
                    bp_graph_incoming_conn_ids[gene.conn_end].append(gene.gene_id)
                else:
                    bp_graph_incoming_conn_ids[gene.conn_end] = [gene.gene_id]

        # Remove all nodes from the 'bp_graph_incoming_conn_ids' dict that have only 1 incoming connection, as this
        # connection is essential and can not be removed without also effectively removing nodes. If a node has more
        # than 1 incoming connection then shuffle those, as they will later be popped.
        bp_graph_incoming_conn_ids_to_remove = list()
        for conn_end, incoming_conn_ids in bp_graph_incoming_conn_ids.items():
            if len(incoming_conn_ids) == 1:
                bp_graph_incoming_conn_ids_to_remove.append(conn_end)
            else:
                random.shuffle(bp_graph_incoming_conn_ids[conn_end])
        for conn_id_to_remove in bp_graph_incoming_conn_ids_to_remove:
            del bp_graph_incoming_conn_ids[conn_id_to_remove]

        # Determine how many conns will be removed based on the total connection count
        number_of_conns_to_rem = math.ceil(max_degree_of_mutation * conn_count)

        # Remove connections in loop until determined number of connections are removed or until no node has 2 incoming
        # connections. Remove connections by randomly choosing a node with more than 1 incoming connections and then
        # removing the associated gene id from the bp graph
        rem_conns_counter = 0
        while rem_conns_counter < number_of_conns_to_rem and len(bp_graph_incoming_conn_ids) > 0:
            rem_conn_end_node = random.choice(tuple(bp_graph_incoming_conn_ids.keys()))
            conn_id_to_remove = bp_graph_incoming_conn_ids[rem_conn_end_node].pop()
            # If node has only 1 incoming connection, remove it from the possible end nodes for future iterations
            if len(bp_graph_incoming_conn_ids[rem_conn_end_node]) == 1:
                del bp_graph_incoming_conn_ids[rem_conn_end_node]

            del blueprint_graph[conn_id_to_remove]
            parent_mutation['removed_genes'].append(conn_id_to_remove)
            rem_conns_counter += 1

        # Create and return the offspring blueprint with the edited blueprint graph having one or multiple connections
        # removed though still having at least 1 connection to each node.
        return self.encoding.create_blueprint(blueprint_graph=blueprint_graph,
                                              optimizer_factory=optimizer_factory,
                                              parent_mutation=parent_mutation)

    def _create_mutated_blueprint_rem_node(self, parent_blueprint, max_degree_of_mutation):
        """"""
        # Copy the parameters of the parent blueprint for the offspring
        blueprint_graph, optimizer_factory = parent_blueprint.copy_parameters()

        # Create the dict that keeps track of the way a blueprint has been mutated
        parent_mutation = {'parent_id': parent_blueprint.get_id(),
                           'mutation': 'rem_node',
                           'removed_genes': list()}

        # Collect all gene_ids of nodes that are not the input or output node (as they are unremovable) and
        # shuffle the list of those node ids for later random popping.
        node_count = 0
        bp_graph_node_ids = list()
        for gene in blueprint_graph.values():
            if isinstance(gene, CoDeepNEATBlueprintNode):
                node_count += 1
                if gene.node != 1 and gene.node != 2:
                    bp_graph_node_ids.append(gene.gene_id)
        random.shuffle(bp_graph_node_ids)

        # Determine how many nodes will be removed based on the total node count
        number_of_nodes_to_rem = math.ceil(max_degree_of_mutation * node_count)

        # Remove nodes in loop until enough nodes are removed or until no node is left to be removed. When removing the
        # node, replace its incoming and outcoming connections with connections from each incoming node to each outgoing
        # node.
        rem_nodes_counter = 0
        while rem_nodes_counter < number_of_nodes_to_rem and len(bp_graph_node_ids) > 0:
            node_id_to_remove = bp_graph_node_ids.pop()
            node_to_remove = blueprint_graph[node_id_to_remove].node

            # Collect all gene ids with connections starting or ending in the chosen node, independent of if the node
            # is enabled or not (as this operation basically reverses the disabling of connections happening when adding
            # instead of removing a node), to be removed later. Also collect all end nodes of the outgoing connections
            # as well as all start nodes of all incoming connections.
            conn_ids_to_remove = list()
            conn_replacement_start_nodes = list()
            conn_replacement_end_nodes = list()
            for gene in blueprint_graph.values():
                if isinstance(gene, CoDeepNEATBlueprintConn):
                    if gene.conn_start == node_to_remove:
                        conn_ids_to_remove.append(gene.gene_id)
                        conn_replacement_end_nodes.append(gene.conn_end)
                    elif gene.conn_end == node_to_remove:
                        conn_ids_to_remove.append(gene.gene_id)
                        conn_replacement_start_nodes.append(gene.conn_start)

            # Remove chosen node and all connections starting or ending in that node from blueprint graph
            del blueprint_graph[node_id_to_remove]
            parent_mutation['removed_genes'].append(node_id_to_remove)
            for id_to_remove in conn_ids_to_remove:
                del blueprint_graph[id_to_remove]
                parent_mutation['removed_genes'].append(id_to_remove)

            # Collect all current connections in blueprint graph to be checked against when creating new connections,
            # in case the connection already exists. This has be done in each iteration as those connections change
            # significantly for each round.
            bp_graph_conns = dict()
            for gene in blueprint_graph.values():
                if isinstance(gene, CoDeepNEATBlueprintConn):
                    bp_graph_conns[(gene.conn_start, gene.conn_end, gene.enabled)] = gene.gene_id

            # Recreate the connections of the removed node by connecting all start nodes of the incoming connections to
            # all end nodes of the outgoing connections. Only recreate the connection if the connection is not already
            # present or if the connection present is disabled
            for new_start_node in conn_replacement_start_nodes:
                for new_end_node in conn_replacement_end_nodes:
                    # Check if a disabled variant of the connection to recreate is in the bp_graph. If so reenable it.
                    if (new_start_node, new_end_node, False) in bp_graph_conns:
                        conn_id_to_reenable = bp_graph_conns[(new_start_node, new_end_node, False)]
                        blueprint_graph[conn_id_to_reenable].set_enabled(True)
                    # Check if a no variant of the connection to recreate is in the bp_graph. If so, create it.
                    if (new_start_node, new_end_node, True) not in bp_graph_conns:
                        gene_id, gene = self.encoding.create_blueprint_conn(conn_start=new_start_node,
                                                                            conn_end=new_end_node)
                        blueprint_graph[gene_id] = gene

        # Create and return the offspring blueprint with the edited blueprint graph having removed nodes which were
        # replaced by a full connection between all incoming and all outgoing nodes.
        return self.encoding.create_blueprint(blueprint_graph=blueprint_graph,
                                              optimizer_factory=optimizer_factory,
                                              parent_mutation=parent_mutation)

    def _create_mutated_blueprint_node_spec(self, parent_blueprint, max_degree_of_mutation):
        """"""
        # Copy the parameters of the parent blueprint for the offspring
        blueprint_graph, optimizer_factory = parent_blueprint.copy_parameters()

        # Create the dict that keeps track of the way a blueprint has been mutated
        parent_mutation = {'parent_id': parent_blueprint.get_id(),
                           'mutation': 'node_spec',
                           'mutated_node_spec': dict()}

        # Identify all non-Input nodes in the blueprint graph by gene ID as the species of those can be mutated
        bp_graph_node_ids = set()
        for gene in blueprint_graph.values():
            if isinstance(gene, CoDeepNEATBlueprintNode) and gene.node != 1:
                bp_graph_node_ids.add(gene.gene_id)

        # Determine the node ids that have their species changed and the available module species to change into
        number_of_node_species_to_change = math.ceil(max_degree_of_mutation * len(bp_graph_node_ids))
        node_ids_to_change_species = random.sample(bp_graph_node_ids, k=number_of_node_species_to_change)
        available_mod_species = tuple(self.mod_species.keys())

        # Traverse through all randomly chosen node ids and change their module species randomly to one of the available
        for node_id_to_change_species in node_ids_to_change_species:
            former_node_species = blueprint_graph[node_id_to_change_species].species
            parent_mutation['mutated_node_spec'][node_id_to_change_species] = former_node_species
            blueprint_graph[node_id_to_change_species].species = random.choice(available_mod_species)

        # Create and return the offspring blueprint with the edited blueprint graph having mutated species
        return self.encoding.create_blueprint(blueprint_graph=blueprint_graph,
                                              optimizer_factory=optimizer_factory,
                                              parent_mutation=parent_mutation)

    def _create_mutated_blueprint_optimizer(self, parent_blueprint):
        """"""
        # Copy the parameters of the parent blueprint for the offspring
        blueprint_graph, optimizer_factory = parent_blueprint.copy_parameters()
        parent_opt_params = optimizer_factory.get_parameters()

        # Create the dict that keeps track of the way a blueprint has been mutated
        parent_mutation = {'parent_id': parent_blueprint.get_id(),
                           'mutation': 'optimizer',
                           'mutated_params': parent_opt_params}

        # Randomly choose type of offspring optimizer and declare container collecting the specific parameters of
        # the offspring optimizer, setting only the chosen optimizer class
        offspring_optimizer_type = random.choice(self.available_optimizers)
        available_opt_params = self.available_opt_params[offspring_optimizer_type]
        offspring_opt_params = {'class_name': offspring_optimizer_type, 'config': dict()}

        if offspring_optimizer_type == parent_opt_params['class_name']:
            ## Mutation of the existing optimizers' parameters ##
            # Traverse each possible parameter option and determine a uniformly random value if its a categorical param
            # or try perturbing the the parent parameter if it is a sortable.
            for opt_param, opt_param_val_range in available_opt_params.items():
                # If the optimizer parameter is a categorical value choose randomly from the list
                if isinstance(opt_param_val_range, list):
                    offspring_opt_params['config'][opt_param] = random.choice(opt_param_val_range)
                # If the optimizer parameter is sortable, create a random value between the min and max values adhering
                # to the configured step
                elif isinstance(opt_param_val_range, dict):
                    if isinstance(opt_param_val_range['min'], int) \
                            and isinstance(opt_param_val_range['max'], int) \
                            and isinstance(opt_param_val_range['step'], int):
                        perturbed_param = int(np.random.normal(loc=parent_opt_params['config'][opt_param],
                                                               scale=opt_param_val_range['stddev']))
                        chosen_opt_param = round_with_step(perturbed_param,
                                                           opt_param_val_range['min'],
                                                           opt_param_val_range['max'],
                                                           opt_param_val_range['step'])
                    elif isinstance(opt_param_val_range['min'], float) \
                            and isinstance(opt_param_val_range['max'], float) \
                            and isinstance(opt_param_val_range['step'], float):
                        perturbed_param = np.random.normal(loc=parent_opt_params['config'][opt_param],
                                                           scale=opt_param_val_range['stddev'])
                        chosen_opt_param = round(round_with_step(perturbed_param,
                                                                 opt_param_val_range['min'],
                                                                 opt_param_val_range['max'],
                                                                 opt_param_val_range['step']), 4)
                    else:
                        raise NotImplementedError(f"Config parameter '{opt_param}' of the {offspring_optimizer_type} "
                                                  f"optimizer section is of type dict though the dict values are not "
                                                  f"of type int or float")
                    offspring_opt_params['config'][opt_param] = chosen_opt_param
                # If the optimizer parameter is a binary value it is specified as a float with the probablity of that
                # parameter being set to True
                elif isinstance(opt_param_val_range, float):
                    offspring_opt_params['config'][opt_param] = random.random() < opt_param_val_range
                else:
                    raise NotImplementedError(f"Config parameter '{opt_param}' of the {offspring_optimizer_type} "
                                              f"optimizer section is not one of the valid types of list, dict or float")

        else:
            ## Creation of a new optimizer with random parameters ##
            # Traverse each possible parameter option and determine a uniformly random value depending on if its a
            # categorical, sortable or boolean value
            for opt_param, opt_param_val_range in available_opt_params.items():
                # If the optimizer parameter is a categorical value choose randomly from the list
                if isinstance(opt_param_val_range, list):
                    offspring_opt_params['config'][opt_param] = random.choice(opt_param_val_range)
                # If the optimizer parameter is sortable, create a random value between the min and max values adhering
                # to the configured step
                elif isinstance(opt_param_val_range, dict):
                    if isinstance(opt_param_val_range['min'], int) \
                            and isinstance(opt_param_val_range['max'], int) \
                            and isinstance(opt_param_val_range['step'], int):
                        opt_param_random = random.randint(opt_param_val_range['min'],
                                                          opt_param_val_range['max'])
                        chosen_opt_param = round_with_step(opt_param_random,
                                                           opt_param_val_range['min'],
                                                           opt_param_val_range['max'],
                                                           opt_param_val_range['step'])
                    elif isinstance(opt_param_val_range['min'], float) \
                            and isinstance(opt_param_val_range['max'], float) \
                            and isinstance(opt_param_val_range['step'], float):
                        opt_param_random = random.uniform(opt_param_val_range['min'],
                                                          opt_param_val_range['max'])
                        chosen_opt_param = round(round_with_step(opt_param_random,
                                                                 opt_param_val_range['min'],
                                                                 opt_param_val_range['max'],
                                                                 opt_param_val_range['step']), 4)
                    else:
                        raise NotImplementedError(f"Config parameter '{opt_param}' of the {offspring_optimizer_type} "
                                                  f"optimizer section is of type dict though the dict values are not "
                                                  f"of type int or float")
                    offspring_opt_params['config'][opt_param] = chosen_opt_param
                # If the optimizer parameter is a binary value it is specified as a float with the probablity of that
                # parameter being set to True
                elif isinstance(opt_param_val_range, float):
                    offspring_opt_params['config'][opt_param] = random.random() < opt_param_val_range
                else:
                    raise NotImplementedError(f"Config parameter '{opt_param}' of the {offspring_optimizer_type} "
                                              f"optimizer section is not one of the valid types of list, dict or float")

        # Create new optimizer through encoding, having either the parent perturbed offspring parameters or randomly
        # new created parameters
        optimizer_factory = self.encoding.create_optimizer_factory(optimizer_parameters=offspring_opt_params)

        # Create and return the offspring blueprint with identical blueprint graph and modified optimizer_factory
        return self.encoding.create_blueprint(blueprint_graph=blueprint_graph,
                                              optimizer_factory=optimizer_factory,
                                              parent_mutation=parent_mutation)

    def _create_crossed_over_blueprint(self, parent_bp_1, parent_bp_2):
        """"""
        # Copy the parameters of both parent blueprints for the offspring
        bp_graph_1, opt_factory_1 = parent_bp_1.copy_parameters()
        bp_graph_2, opt_factory_2 = parent_bp_2.copy_parameters()

        # Create the dict that keeps track of the way a blueprint has been mutated
        parent_mutation = {'parent_id': (parent_bp_1.get_id(), parent_bp_2.get_id()),
                           'mutation': 'crossover',
                           'gene_parent': dict(),
                           'optimizer_parent': None}

        # Create quickly searchable sets of gene ids to know about the overlap of genes in both blueprint graphs
        bp_graph_1_ids = set(bp_graph_1.keys())
        bp_graph_2_ids = set(bp_graph_2.keys())
        all_bp_graph_ids = bp_graph_1_ids.union(bp_graph_2_ids)

        # Create offspring blueprint graph by traversing all blueprint graph ids an copying over all genes that are
        # exclusive to either blueprint graph and randomly choosing the gene to copy over that is present in both graphs
        offspring_bp_graph = dict()
        for gene_id in all_bp_graph_ids:
            if gene_id in bp_graph_1_ids and gene_id in bp_graph_2_ids:
                if random.randint(0, 1) == 0:
                    offspring_bp_graph[gene_id] = bp_graph_1[gene_id]
                    parent_mutation['gene_parent'][gene_id] = parent_bp_1.get_id()
                else:
                    offspring_bp_graph[gene_id] = bp_graph_2[gene_id]
                    parent_mutation['gene_parent'][gene_id] = parent_bp_2.get_id()
            elif gene_id in bp_graph_1_ids:
                offspring_bp_graph[gene_id] = bp_graph_1[gene_id]
                parent_mutation['gene_parent'][gene_id] = parent_bp_1.get_id()
            else:  # if gene_id in bp_graph_2_ids
                offspring_bp_graph[gene_id] = bp_graph_2[gene_id]
                parent_mutation['gene_parent'][gene_id] = parent_bp_2.get_id()

        # For the optimizer factory choose the one from the fitter parent blueprint
        if parent_bp_1.get_fitness() > parent_bp_2.get_fitness():
            offspring_opt_factory = opt_factory_1
            parent_mutation['optimizer_parent'] = parent_bp_1.get_id()
        else:
            offspring_opt_factory = opt_factory_2
            parent_mutation['optimizer_parent'] = parent_bp_2.get_id()

        # Create and return the offspring blueprint with crossed over blueprint graph and optimizer_factory of the
        # fitter parent
        return self.encoding.create_blueprint(blueprint_graph=offspring_bp_graph,
                                              optimizer_factory=offspring_opt_factory,
                                              parent_mutation=parent_mutation)
