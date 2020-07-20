import ast

from .codeepneat_genome import CoDeepNEATGenome
from .codeepneat_optimizer_factory import OptimizerFactory
from .codeepneat_blueprint import CoDeepNEATBlueprint, CoDeepNEATBlueprintNode, CoDeepNEATBlueprintConn
from .modules.codeepneat_module_base import CoDeepNEATModuleBase
from ..base_encoding import BaseEncoding

# Import Association dict of the module string name to its implementation class
from .modules.codeepneat_module_association import MODULES


class CoDeepNEATEncoding(BaseEncoding):
    """"""

    def __init__(self, dtype, saved_state=None):
        """"""
        # Register parameters
        self.dtype = dtype

        # Initialize internal counter variables
        self.genome_id_counter = 0
        self.mod_id_counter = 0
        self.bp_id_counter = 0
        self.bp_gene_id_counter = 0

        # Initialize container that maps a blueprint gene to its assigned blueprint gene id. If a new blueprint gene is
        # created will this container allow to check if that gene has already been created before and has been assigned
        # a unique gene id before. If the blueprint gene has already been created before will the same gene id be used.
        self.gene_to_gene_id = dict()

        # Initialize a counter for nodes and a history container, assigning the tuple of connection start and end a
        # previously assigned node or new node if not yet present in history.
        self.node_counter = 2
        self.conn_split_history = dict()

        # If saved_state provided, load the parameters
        if saved_state is not None:
            self._load_state(saved_state)

    def create_initial_module(self, mod_type, config_params) -> (int, CoDeepNEATModuleBase):
        """"""
        # Determine module ID and set the parent mutation to 'init' notification
        self.mod_id_counter += 1
        parent_mutation = {'parent_id': None,
                           'mutation': 'init'}

        return self.mod_id_counter, MODULES[mod_type](config_params=config_params,
                                                      module_id=self.mod_id_counter,
                                                      parent_mutation=parent_mutation,
                                                      dtype=self.dtype,
                                                      self_initialization_flag=True)

    def create_mutated_module(self, parent_module, max_degree_of_mutation) -> (int, CoDeepNEATModuleBase):
        """"""
        self.mod_id_counter += 1
        return self.mod_id_counter, parent_module.create_mutation(self.mod_id_counter,
                                                                  max_degree_of_mutation)

    def create_crossover_module(self,
                                parent_module_1,
                                parent_module_2,
                                max_degree_of_mutation) -> (int, CoDeepNEATModuleBase):
        """"""
        self.mod_id_counter += 1
        # Determine fitter parent module and call internal crossover function of fitter parent
        if parent_module_1.get_fitness() >= parent_module_2.get_fitness():
            return self.mod_id_counter, parent_module_1.create_crossover(self.mod_id_counter,
                                                                         parent_module_2,
                                                                         max_degree_of_mutation)
        else:
            return self.mod_id_counter, parent_module_2.create_crossover(self.mod_id_counter,
                                                                         parent_module_1,
                                                                         max_degree_of_mutation)

    def create_blueprint_node(self, node, species) -> (int, CoDeepNEATBlueprintNode):
        """"""
        gene_key = (node,)
        if gene_key not in self.gene_to_gene_id:
            self.bp_gene_id_counter += 1
            self.gene_to_gene_id[gene_key] = self.bp_gene_id_counter

        bp_gene_id = self.gene_to_gene_id[gene_key]
        return bp_gene_id, CoDeepNEATBlueprintNode(bp_gene_id, node, species)

    def create_node_for_split(self, conn_start, conn_end) -> int:
        """"""
        conn_key = (conn_start, conn_end)
        if conn_key not in self.conn_split_history:
            self.node_counter += 1
            self.conn_split_history[conn_key] = self.node_counter

        return self.conn_split_history[conn_key]

    def create_blueprint_conn(self, conn_start, conn_end) -> (int, CoDeepNEATBlueprintConn):
        """"""
        gene_key = (conn_start, conn_end)
        if gene_key not in self.gene_to_gene_id:
            self.bp_gene_id_counter += 1
            self.gene_to_gene_id[gene_key] = self.bp_gene_id_counter

        bp_gene_id = self.gene_to_gene_id[gene_key]
        return bp_gene_id, CoDeepNEATBlueprintConn(bp_gene_id, conn_start, conn_end)

    def create_blueprint(self,
                         blueprint_graph,
                         optimizer_factory,
                         parent_mutation) -> (int, CoDeepNEATBlueprint):
        """"""
        self.bp_id_counter += 1
        return self.bp_id_counter, CoDeepNEATBlueprint(blueprint_id=self.bp_id_counter,
                                                       parent_mutation=parent_mutation,
                                                       blueprint_graph=blueprint_graph,
                                                       optimizer_factory=optimizer_factory)

    def create_genome(self,
                      blueprint,
                      bp_assigned_modules,
                      output_layers,
                      input_shape,
                      generation) -> (int, CoDeepNEATGenome):
        """"""
        self.genome_id_counter += 1
        # Genome genotype: (blueprint, bp_assigned_modules, output_layers)
        return self.genome_id_counter, CoDeepNEATGenome(genome_id=self.genome_id_counter,
                                                        blueprint=blueprint,
                                                        bp_assigned_modules=bp_assigned_modules,
                                                        output_layers=output_layers,
                                                        input_shape=input_shape,
                                                        dtype=self.dtype,
                                                        origin_generation=generation)

    @staticmethod
    def create_optimizer_factory(optimizer_parameters) -> OptimizerFactory:
        """"""
        return OptimizerFactory(optimizer_parameters)

    def serialize_state(self) -> dict:
        """"""
        # Convert keys of gene_to_gene_id and conn_split_history dicts to strings as tuples not elligible for json
        # serialization
        serialized_gene_to_gene_id = dict()
        for key, value in self.gene_to_gene_id.items():
            serializable_key = str(key)
            serialized_gene_to_gene_id[serializable_key] = value
        serialized_conn_split_history = dict()
        for key, value in self.conn_split_history.items():
            serializable_key = str(key)
            serialized_conn_split_history[serializable_key] = value

        return {
            'genome_id_counter': self.genome_id_counter,
            'mod_id_counter': self.mod_id_counter,
            'bp_id_counter': self.bp_id_counter,
            'bp_gene_id_counter': self.bp_gene_id_counter,
            'gene_to_gene_id': serialized_gene_to_gene_id,
            'node_counter': self.node_counter,
            'conn_split_history': serialized_conn_split_history
        }

    def _load_state(self, saved_state):
        """"""
        # Convert keys of serialized gene_to_gene_id and conn_split_history dicts back to tuples
        for key, value in saved_state['gene_to_gene_id'].items():
            deserialized_key = ast.literal_eval(key)
            self.gene_to_gene_id[deserialized_key] = value
        for key, value in saved_state['conn_split_history'].items():
            deserialized_key = ast.literal_eval(key)
            self.conn_split_history[deserialized_key] = value

        # Deserialize rest of encoding state
        self.genome_id_counter = saved_state['genome_id_counter']
        self.mod_id_counter = saved_state['mod_id_counter']
        self.bp_id_counter = saved_state['bp_id_counter']
        self.bp_gene_id_counter = saved_state['bp_gene_id_counter']
        self.node_counter = saved_state['node_counter']
