CoDeepNEAT Configuration
========================

**[WORK IN PROGRESS]**



[EVALUATION] Config Parameters
------------------------------

``epochs``
  **Value Range**: int > 0

  **Description**: Specifies the amount of epochs a genome phenotype is to be trained on the environment before evaluating its fitness.


``batch_size``
  **Value Range**: int > 0 | None

  **Description**: Supplied batch_size value for the model.fit function. batch_size is the number of training examples used for a single iteration of backpropagating the gradient of the loss function.


``preprocessing``
  **Value Range**: -

  **Description**: <FEATURE STILL IN DEVELOPMENT>

--------------------------------------------------------------------------------



[POPULATION] Config Parameters
------------------------------

``bp_pop_size``
  **Value Range**: int > 0

  **Description**: Size of the Blueprint population throughout the evolution. The population size is constant.


``mod_pop_size``
  **Value Range**: int > 0

  **Description**: Size of the Module population throughout the evolution. The population size is constant.


``genomes_per_bp``
  **Value Range**: int > 0

  **Description**: Specifies the amount of genomes that are created from blueprints and modules for the evaluation phase of each generation. Each blueprint is accordingly often used as the base topology to create genomes.

--------------------------------------------------------------------------------



[GENOME] Config Parameters
--------------------------

``dtype``
  **Value Range**: valid Tensorflow datatype

  **Description**: Datatype of the genome phenotype, being a Tensorflow model.


``available_modules``
  **Value Range**: list of strings of valid TFNE CoDeepNEAT modules

  **Description**: Specifies the module types that will be created during the CoDeepNEAT evolution. The association of module string name to module implementation is in a simple association file within the CoDeepNEAT encoding. This association file registers the names of all pre-implemented CoDeepNEAT modules and can easily be extended to register custom-created modules.


``available_optimizers``
  **Value Range**: list of strings of valid Tensorflow Optimizers

  **Description**: Specifies the possibly used optimizers that are associated with CoDeepNEAT blueprints. Valid values are string representations of all Tensorflow Optimizers, as TFNE uses Tensorflow deserialization of the optimizers.


``output_layers``
  **Value Range**: list of dictionaries that represent deserializable Tensorflow layers

  **Description**: Specifies the layers and their configuration that will be appended to the evolved CoDeepNEAT genome in order to control the output despite fitness oriented evolution of the phenotype. The output layers will be appended to the genome in the same order in which they are listed.

--------------------------------------------------------------------------------



[MODULE_SPECIATION] Config Parameters
-------------------------------------

``mod_spec_type``
  **Value Range**: 'basic' | 'param-distance-fixed' | 'param-distance-dynamic'

  **Description**: Sets speciation method for modules. Can be set to either a basic speciation; a speciation based on the parameter distance of the modules with fixed parameter distance; or a speciation based on the parameter distance of the modules but with dynamically changing parameter distance. For details of these speciation methods, check the CoDeepNEAT specification.


``mod_spec_species_count``
  **Value Range**: int > 0

  **Description**: **[Only applicable when using 'param-distance-dynamic' speciation]** Specifies the desired species count the dynamic parameter distance speciation scheme should aim for when adjusting the species distance. The species count considers the total amount of species and is not considered per module type.


``mod_spec_distance``
  **Value Range**: 1.0 >= float >= 0

  **Description**: **[Only applicable when using 'param-distance-fixed' or 'param-distance-dynamic' speciation]** Specifies minimum distance of 2 modules such that they are classified into 2 different species.


``mod_spec_mod_elitism``
  **Value Range**: int > 0

  **Description**: Specifies the amount of best modules in each species that will be carried over unchanged into the next generation after the evolution. The module elitism has to be at least 1 in order to carry over at least one species representative upon which newly evolved modules are judged if they belong into the same species.


``mod_spec_min_offspring``
  **Value Range**: int >= 0

  **Description**: Specifies the minimum amount of newly generated offspring for each species, in case the average fitness of the species becomes so relatively low that it isn't assigned offspring otherwise.


``mod_spec_reprod_thres``
  **Value Range**: 1.0 >= float >= 0

  **Description**: Specifies the minimum relative fitness threshold of a module compared with other modules in its species in order for the module to be considered a possible parent for reproduction. E.g. if the value 0.4 is choosen then for a module to be considered an elligible parent for the species its fitness has be higher than the bottom 40 percent of the species (or in other words: it has to belong to the top 60% of modules in the species).


``mod_spec_max_stagnation``
  **Value Range**: int > 0

  **Description**: **[Only applicable when using 'param-distance-fixed' or 'param-distance-dynamic' speciation]** Specifies the maximum number of generations a species does not improve its average fitness before it will be considered stagnating and therefore will go extinct. This stagnation is defined as not producing in either of the last x generations an average fitness better than the fitness x generations ago.


``mod_spec_species_elitism``
  **Value Range**: int >= 0

  **Description**: **[Only applicable when using 'param-distance-fixed' or 'param-distance-dynamic' speciation]** Specifies the minimum amount of species that are to survive, regardless of the consideration that they are stagnating or not. The minimum amount of surving species are the best of the current generation.


``mod_spec_rebase_repr``
  **Value Range**: bool

  **Description**: **[Only applicable when using 'param-distance-fixed' or 'param-distance-dynamic' speciation]** Specifies if after each evolution the species representatives should be rebased to the best module of the species that also holds the minimal distance to all other species representatives as specified in via ``mod_spec_species_distance``.


``mod_spec_reinit_extinct``
  **Value Range**: bool

  **Description**: **[Only applicable when using 'param-distance-fixed' or 'param-distance-dynamic' speciation]** Specifies if the population size occupied by a species should be reinitialized to new modules upon species extinction or if the population size occupied by the extinct species should be divided among the remaining species.

--------------------------------------------------------------------------------



[MODULE_EVOLUTION] Config Parameters
------------------------------------

``mod_max_mutation``
  **Value Range**: 1.0 >= float >= 0

  **Description**: Specifies the maximum percentage to which a module is mutated during evolution from one generation to the next.


``mod_mutation_prob``
  **Value Range**: 1.0 >= float >= 0

  **Description**: Specifies the probability that a new module is evolved through mutation of an elligible parent module. Evolution probabilities of modules must add up to 1.


``mod_crossover_prob``
  **Value Range**: 1.0 >= float >= 0

  **Description**: Specifies the probability that a new module is evolved through crossover of two elligible parent modules. Evolution probabilities of modules must add up to 1.

--------------------------------------------------------------------------------



[BP_SPECIATION] Config Parameters
---------------------------------

``bp_spec_type``
  **Value Range**: 'basic' | 'gene-overlap-fixed' | 'gene-overlap-dynamic'

  **Description**: Sets speciation method for blueprints. Can be set to either a basic speciation; a speciation based on the gene overlap of the blueprints with fixed overlap distance; or a speciation based on the gene overlap of the blueprints but with dynamically changing overlap distance. For details of these speciation methods, check the CoDeepNEAT specification.


``bp_spec_species_count``
  **Value Range**: int > 0

  **Description**: **[Only applicable when using 'gene-overlap-dynamic' speciation]** Specifies the desired species count the dynamic gene overlap distance speciation scheme should aim for when adjusting the species.


``bp_spec_distance``
  **Value Range**: 1.0 >= float >= 0

  **Description**: **[Only applicable when using 'gene-overlap-fixed' or 'gene-overlap-dynamic' speciation]** Specifies the minimum distance of 2 blueprints such that they are classified into 2 different species.


``bp_spec_bp_elitism``
  **Value Range**: int > 0

  **Description**: Specifies the amount of best blueprints in each species that will be carried over unchanged into the next generation after the evolution. The blueprint elitism has to be at least 1 in order to carry over at least one species representative upon which newly evolved modules are judged if they belong into the same species.


``bp_spec_min_offspring``
  **Value Range**: int >= 0

  **Description**: Specifies the minimum amount of newly generated offspring for each species, in case the average fitness of the species becomes so relatively low that it isn't assigned offspring otherwise.


``bp_spec_reprod_thres``
  **Value Range**: 1.0 >= float >= 0

  **Description**: Specifies the minimum relative fitness threshold of a blueprint compared with other blueprints in its species in order for the blueprint to be considered a possible parent for reproduction. E.g. if the value 0.4 is choosen then for a blueprint to be considered an elligible parent for the species its fitness has to be higher than the bottom 40 percent of the species (or in other words: it has to belong to the top 60% of blueprints in the species).


``bp_spec_max_stagnation``
  **Value Range**: int > 0

  **Description**: **[Only applicable when using 'gene-overlap-fixed' or 'gene-overlap-dynamic' speciation]** Specifies the maximum number of generations a species does not improve its average fitness before it will be considered stagnating and therefore will go extinct. This stagnation is defined as not producing in either of the last x generations an average fitness better than the fitness x generations ago.


``bp_spec_species_elitism``
  **Value Range**: int >= 0

  **Description**: **[Only applicable when using 'gene-overlap-fixed' or 'gene-overlap-dynamic' speciation]** Specifies the minimum amount of species that are to survive, regardless of the consideration that they are stagnating or not. The minimum amount of surviving species are the ebst of the current generation.


``bp_spec_rebase_repr``
  **Value Range**: bool

  **Description**: **[Only applicable when using 'gene-overlap-fixed' or 'gene-overlap-dynamic' speciation]** Specifies if after each evolution the species representatives should be rebased to the best blueprint of the species that also holds the minimal distance to all other species representatives as specified via ``bp_spec_species_distance``.


``bp_spec_reinit_extinct``
  **Value Range**: bool

  **Description**: **[Only applicable when using 'gene-overlap-fixed' or 'gene-overlap-dynamic' speciation]** Specifies if the population size occupied by a species should be reinitialized to new blueprints upon species extinction or if the population size occupied by the extinct species should be divided among the remaining species.

--------------------------------------------------------------------------------



[BP_EVOLUTION] Config Parameters
--------------------------------

``bp_max_mutation``
  **Value Range**: 1.0 >= float >= 0

  **Description**: Specifies the maximum percentage to which a blueprint is mutated during evolution from one generation to the next.


``bp_mutation_add_conn_prob``
  **Value Range**: 1.0 >= float >= 0

  **Description**: Specifies the probability that a new blueprint is evolved by adding a connection to an elligible parent blueprint. Evolution probabilities of blueprints must add up to 1.


``bp_mutation_add_node_prob``
  **Value Range**: 1.0 >= float >= 0

  **Description**: Specifies the probability that a new blueprint is evolved by adding a node to an elligible parent blueprint. Evolution probabilities of blueprints must add up to 1.


``bp_mutation_rem_conn_prob``
  **Value Range**: 1.0 >= float >= 0

  **Description**: Specifies the probability that a new blueprint is evolved by removing a connection from an elligible parent blueprint. Evolution probabilities of blueprints must add up to 1.


``bp_mutation_rem_node_prob``
  **Value Range**: 1.0 >= float >= 0

  **Description**: Specifies the probability that a new blueprint is evolved by removing a node from an elligible parent blueprint. Evolution probabilities of blueprints must add up to 1.


``bp_mutation_node_spec_prob``
  **Value Range**: 1.0 >= float >= 0

  **Description**: Specifies the probability that a new blueprint is evolved by mutating the species of the blueprint nodes from an elligible parent blueprint. Evolution probabilities of blueprints must add up to 1.


``bp_mutation_optimizer_prob``
  **Value Range**: 1.0 >= float >= 0

  **Description**: Specifies the probability that a new blueprint is evolved by mutating the config options of the blueprint associated optimizer of an elligible parent blueprint. Evolution probabilities of blueprints must add up to 1.


``bp_crossover_prob``
  **Value Range**: 1.0 >= float >= 0

  **Description**: Specifies the probability that a new blueprint is evolved by crossing over 2 elligible parent blueprints. Evolution probabilities of blueprints must add up to 1.

--------------------------------------------------------------------------------



[MODULE_<MODULE>] Config Parameters
-----------------------------------

Lorem ipsum dolor sit amet

--------------------------------------------------------------------------------



[OPTIMIZER_<OPTIMIZER>] Config Parameters
-----------------------------------------

Lorem ipsum dolor sit amet

