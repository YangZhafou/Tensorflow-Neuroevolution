from tfne.encodings.codeepneat import CoDeepNEATGenome
from tfne.encodings.codeepneat import CoDeepNEATBlueprint
from tfne.encodings.codeepneat.codeepneat_blueprint import CoDeepNEATBlueprintNode, CoDeepNEATBlueprintConn
from tfne.encodings.codeepneat.codeepneat_optimizer_factory import OptimizerFactory
from tfne.encodings.codeepneat.modules.codeepneat_module_base import CoDeepNEATModuleBase
from tfne.encodings.codeepneat.modules.codeepneat_module_association import MODULES
from tfne.populations.codeepneat.codeepneat_population import CoDeepNEATPopulation


def deserialize_codeepneat_population(serialized_population, dtype, module_config_params=None) -> CoDeepNEATPopulation:
    """"""
    # Deserialize all saved population internal evolution information except for the modules, blueprints and best
    # genome, as they have to be deserialized seperately. Save all in the initial state dict of the CoDeepNEAT pop.
    initial_state = dict()

    initial_state['generation_counter'] = serialized_population['generation_counter']
    initial_state['mod_species'] = {int(k): v for k, v in serialized_population['mod_species'].items()}
    initial_state['mod_species_repr'] = {int(k): v for k, v in serialized_population['mod_species_repr'].items()}
    initial_state['mod_species_fitness_history'] = {int(k1): {int(k2): v2 for k2, v2 in v1.items()}
                                                    for k1, v1
                                                    in serialized_population['mod_species_fitness_history'].items()}
    initial_state['mod_species_counter'] = serialized_population['mod_species_counter']
    initial_state['bp_species'] = {int(k): v for k, v in serialized_population['bp_species'].items()}
    initial_state['bp_species_repr'] = {int(k): v for k, v in serialized_population['bp_species_repr'].items()}
    initial_state['bp_species_fitness_history'] = {int(k1): {int(k2): v2 for k2, v2 in v1.items()}
                                                   for k1, v1
                                                   in serialized_population['bp_species_fitness_history'].items()}
    initial_state['bp_species_counter'] = serialized_population['bp_species_counter']
    initial_state['best_fitness'] = serialized_population['best_fitness']

    # Deserialize modules
    initial_state['modules'] = dict()
    for mod_id, mod_params in serialized_population['modules'].items():
        initial_state['modules'][int(mod_id)] = deserialize_codeepneat_module(mod_params, dtype, module_config_params)

    # Deserialize blueprints
    initial_state['blueprints'] = dict()
    for bp_id, bp_params in serialized_population['blueprints'].items():
        initial_state['blueprints'][int(bp_id)] = deserialize_codeepneat_blueprint(bp_params)

    # Deserialize best genome
    initial_state['best_genome'] = deserialize_codeepneat_genome(serialized_population['best_genome'],
                                                                 dtype,
                                                                 module_config_params)

    return CoDeepNEATPopulation(initial_state=initial_state)


def deserialize_codeepneat_genome(serialized_genome, dtype, module_config_params=None) -> CoDeepNEATGenome:
    """"""
    # Deserialize underlying blueprint of genome
    blueprint = deserialize_codeepneat_blueprint(serialized_genome['blueprint'])

    # Deserialize bp_assigned_mods
    bp_assigned_mods = dict()
    for spec, assigned_mod in serialized_genome['bp_assigned_modules'].items():
        bp_assigned_mods[int(spec)] = deserialize_codeepneat_module(assigned_mod, dtype, module_config_params)

    return CoDeepNEATGenome(genome_id=serialized_genome['genome_id'],
                            blueprint=blueprint,
                            bp_assigned_modules=bp_assigned_mods,
                            output_layers=serialized_genome['output_layers'],
                            input_shape=tuple(serialized_genome['input_shape']),
                            dtype=dtype,
                            origin_generation=serialized_genome['origin_generation'])


def deserialize_codeepneat_module(mod_params, dtype, module_config_params=None) -> CoDeepNEATModuleBase:
    """"""
    mod_type = mod_params['module_type']
    del mod_params['module_type']
    # If module is deserialized only for the purpose of inspection/visualization/layer creation, no module config params
    # are required, as those are only needed for mutation/crossover. Therefore, if no module config params are supplied
    # create module accordingly
    if module_config_params is None:
        return MODULES[mod_type](config_params=None,
                                 dtype=dtype,
                                 **mod_params)
    else:
        return MODULES[mod_type](config_params=module_config_params[mod_type],
                                 dtype=dtype,
                                 **mod_params)


def deserialize_codeepneat_blueprint(bp_params) -> CoDeepNEATBlueprint:
    """"""
    # Deserialize Blueprint graph
    bp_graph = dict()
    for gene_id, gene_params in bp_params['blueprint_graph'].items():
        if 'node' in gene_params:
            bp_graph[int(gene_id)] = CoDeepNEATBlueprintNode(gene_id, gene_params['node'], gene_params['species'])
        else:
            bp_graph[int(gene_id)] = CoDeepNEATBlueprintConn(gene_id,
                                                             gene_params['conn_start'],
                                                             gene_params['conn_end'],
                                                             gene_params['enabled'])
    # Recreate optimizer factory
    optimizer_factory = OptimizerFactory(bp_params['optimizer_factory'])

    # Recreate deserialized Blueprint
    return CoDeepNEATBlueprint(bp_params['blueprint_id'],
                               bp_params['parent_mutation'],
                               bp_graph,
                               optimizer_factory)
