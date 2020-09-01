..
   Define line break and bullet command for this section, as necessary for
   properly formatted list in tables

.. |br| raw:: html

   <br />

.. |bullet| unicode:: \u2022

CoDeepNEAT Specification
========================

.. note:: This documentation solely lists the algorithm & encoding specifications without concerning itself with the validity or potential of the specific choices that make up the CoDeepNEAT method.

.. warning::  This documentation outlines the CoDeepNEAT algorithm & encoding specifications as understood by the TFNE project. While the TFNE project aims to stay as close as possible to the original specification, does it also aim to be a superset of the configuration options of the original specification. This specification also concretizes the algorithm specification if the original specification is too vague and no code was supplied. If you find an issue with the specification or the implementation details please contact tfne@paulpauls.de. Thank you.


--------------------------------------------------------------------------------

CoDeepNEAT Encoding
-------------------

The genotype of a CoDeepNEAT genome is made up of 2 essential parts. The first part is the CoDeepNEAT blueprint, specifying the ANN topology and the training hyperparameters that will be associated with the genome. The second part is a collection of small fully functional deep neural networks, termed the CoDeepNEAT modules, that will replace the nodes in the blueprint specified ANN topology. It is important to understand these two essential parts, what they entail, their exact contribution to the final genome and how exactly they are evolved in order to fully understand the CoDeepNEAT encoding and resulting genomes.


CoDeepNEAT Blueprint
~~~~~~~~~~~~~~~~~~~~

+---------------------------------------------+----------------------------------+
| Blueprint genotype                          | |bullet| Blueprint graph |br|    |
|                                             | |bullet| Optimizer configuration |
+---------------------------------------------+----------------------------------+

A blueprint is the fundamental building block of a CoDeepNEAT genome, specifying the genome's basic ANN topology as well as all its hyperparameters that may be associated with that genome.

In TFNE the current extent of hyperparameters saved by blueprints is a full configuration of a Tensorflow optimizer, specifying all variables required for the training of the genome phenotype TF model. Additional hyperparameters such as possible training preprocessing operations can also be included, though are currently not part of TFNE's CoDeepNEAT. This Tensorflow optimizer configuration is the first part of the blueprint's genotype.

The second part of the blueprint genotype is the graph that is specifying the basic ANN topology. This graph will be referred to as the blueprint graph. The blueprint graph is a collection of node and connection *gene* instances. In TFNE, those node and connection gene classes are defined as listed below, demonstrating the extent of the information they contain. The purpose and functionality of these blueprint graph genes is very similar to the functionality of genome genes in the original NEAT algorithm [see `NEAT <../neat/neat-overview.html>`_], as they are adapted from those. The difference being that each node gene stores a module species and each connection gene merely indicates connections between nodes but not associated connection weights. As in NEAT is TFNE currently restricting the blueprint graph to representing a feedforward graph, though a later addition to support full recurrent graphs is planned.

.. code-block:: python

    class CoDeepNEATBlueprintNode:
        def __init__(self, gene_id, node, species):
            self.gene_id = gene_id
            self.node = node
            self.species = species

    class CoDeepNEATBlueprintConn:
        def __init__(self, gene_id, conn_start, conn_end, enabled=True):
            self.gene_id = gene_id
            self.conn_start = conn_start
            self.conn_end = conn_end
            self.enabled = enabled

        def set_enabled(self, enabled):
            self.enabled = enabled


Each gene is assigned an ID. This ID is not unique to each gene instance but unique to each configuration of (node, species) or (conn_start, conn_end) respectively. This behaviour is important to adhere to the principle of *Historical Markings* [see `NEAT <../neat/neat-overview.html>`_]. The ``node`` value is graph-unique integer identifier for each node and is specified in ``conn_start`` and ``conn_end`` as the start- and endpoint of the connection. Each connection can be disabled through a mutation or crossover. The ``species`` value is the ID of an existing, non-extinct module species and is relevant for the later assembly of the final genome phenotype model, combining blueprint and modules.


CoDeepNEAT Module
~~~~~~~~~~~~~~~~~

+---------------------------------------------+--------------------------------+
| Module genotype                             | |bullet| Merge method |br|     |
|                                             | |bullet| Module DNN parameters |
+---------------------------------------------+--------------------------------+

A CoDeepNEAT module is a class of small deep neural networks that can take on only limited complexity. The ANN topology as well as the parameters of the ANN layers are determined through a uniform set of parameters serving as the module genotype. However, since the set of parameters for a module instance is uniform and bounded, does this prevent the topology to become overly complex as only limited information can be stored in a CoDeepNEAT module instance. On the other hand does this allow for a direct comparison of module parameters as each module instance stores values for each module parameter.

A CoDeepNEAT module is obviously a very general concept and its specifics are highly dependent on the concrete implementation. A simple example module is the pre-implemented ``DenseDropout`` module [see `CoDeepNEAT Modules <./codeepneat-modules.html>`_], whose genotype storing has been implemented in TFNE as listed below. The module stores multiple parameters for the initial dense layer, a flag determining the presence of an optional subsequent dropout layer as well as parameters for that subsequent dropout layer. This simple class of module can only represent 2 possible ANN topologies, though it can potentially represent any valid parameter combination for the layer configuration.

.. code-block:: python

    class CoDeepNEATModuleDenseDropout(CoDeepNEATModuleBase):

        ...

        # Register the module parameters
        self.merge_method = merge_method
        self.units = units
        self.activation = activation
        self.kernel_init = kernel_init
        self.bias_init = bias_init
        self.dropout_flag = dropout_flag
        self.dropout_rate = dropout_rate


The uniformity of module parameters mentioned above simplifies evolutionary operations such as speciation, mutation and crossover. More importantly however does the resulting limited complexity resemble the concept of CoDeepNEAT in that it aims to evolve effective small DNNs in a repetitive network topology quickly in order to exploit the same repetitive structure in the problem environment. These repetitive and deep structures are seen in many successful recent DNNs.

The module genotype also requires a specification of a specific merge method as well as a method for downsampling input for this module. Both methods become relevant when combining blueprint and modules in the genome assembly. As the creation of an appropriate downsampling layer can be very complex is this functionality coded into the module itself in TFNE and is therefore not part of the genotype.

The section `CoDeepNEAT Modules <./codeepneat-modules.html>`_ introduces multiple pre-implemented modules provided by TFNE.


CoDeepNEAT Genome
~~~~~~~~~~~~~~~~~

+---------------------------------------------+-----------------------------------------------------------+
| Genome genotype                             | |bullet| Blueprint |br|                                   |
|                                             | |bullet| 1 Module for each Mod species present in BP |br| |
|                                             | |bullet| Output layers                                    |
+---------------------------------------------+-----------------------------------------------------------+

A CoDeepNEAT genome is comprised of 1 blueprint and 1 module for each module species that is present in the nodes of the BP graph. The genome adopts all hyperparameters from the associated blueprint, which in TFNE implies the configuration of the TF optimizer used in the eventual model training.

The phenotype of the genome is a Tensorflow model that is assembled by combining the blueprint graph and modules. The basic topology of the phenotype model is dictated by the graph represented in blueprint graph. TFNE currently only supporting feedforward graphs, though we hope to implement recurrent graphs soon. Each node in that blueprint graph will be replaced by a module, depending on the ``species`` value of the node. As modules themselves are small DNNs will the resulting graph be a full DNN consisting of multiple small DNNs that are connected to each other. If a module has multiple inputs will the inputs be merged according to the ``merge_method`` genotype value of the module. If a module has an input with mismatching dimensions will the input be downsampled through the specific downsampling method associated with the module type, which in TFNE can be accessed through ``create_downsampling_layer(...)``. The genotype graph is fully assembled when appending a predefined set of output layers to the final layer of the evolved graph, in order to conform with the required output of the problem environment.

The modules that are chosen to replace the graph nodes based on their ``species`` value, are selected as follows: Each ``species`` value in the nodes of the blueprint graph is identifying an existing, non-extinct module species (a species is a cluster of similar members, see `CoDeepNEAT Evolution <./codeepneat-specification.html#evolution>`_ below). For each ``species`` value that is present in the blueprint graph, select one specific module from that identified module species. The created association between ``species`` ID value and specific module is the above mentioned part of the genome genotype. In the phenotype TF model assembly replace each node with the same corresponding specific module. This way beneficial topological structure and parametrized layers are replicated throughout the final TF model in order to exploit the same repetitive structure in the problem environment.

To summarize is the exact process of translating the genome genotype into the phenotype model illustrated below:


**[ILLUSTRATION HERE]**


--------------------------------------------------------------------------------

CoDeepNEAT Algorithm
--------------------

Unlike traditional neuroevolution algorithms does the CoDeepNEAT algorithm not operate on and evolve genomes directly, but instead primarily operates on blueprints and modules. Genomes are only assembled during the evaluation in order to determine the fitness of the associated blueprints and modules.


Initialization
~~~~~~~~~~~~~~

**see CoDeepNEAT.initialize_population(...)**

CoDeepNEAT initializes a minimal population as it has been modeled after NEAT, an additive neuroevolution algorithm. The initialization is therefore very simple. All modules of the population are initialized with random parameters and assigned to a single species.

All blueprints are initialized with a minimal graph of 2 nodes and a connection. The first node is node 1, serving as a special, non mutateable, input layer. The second node is node 2, serving as the output layer and being assigned a ``species`` value identifying the single species ID all initialized modules have been assigned to. The hyperparameters of all blueprints are initialized with random parameters. As done for modules will all blueprints of the population be assigned to a single initial blueprint species.


Evaluation
~~~~~~~~~~

**[see CoDeepNEAT.evaluate_population(...)]**

As the CoDeepNEAT population consists exclusively of blueprints and modules is the
The CoDeepNEAT population is evaluated by assembling genomes from the population of blueprints and modules, evaluating those genomes and then transferring the achieved genome fitness back to their blueprint and module components.

For each blueprint in the population the algorithm assembles a predefined number of genomes that take that blueprint as their base. For each of these genomes that are to be assembled, specific modules of the referenced blueprint graph node species are chosen randomly from the module species. That blueprint, randomly chosen modules of all referenced module species as well as the constant set of output layers constitute a full genome genotype and generate a phenotype TF model according to the genome encoding `genome encoding <./codeepneat-specification.html#codeepneat-genome>`_ above. The assembled genome is then applied to the evaluation environment and assigned the recsulting fitness score.

If due to the random choice of modules for the blueprint graph an invalid TF model is generated from the genome genotype, the assembled genome is assigned a fitness score of 0. As the evolutionary process evolves blueprints and modules seperately is it impossible to guarantee a genotype that results in a valid TF model when both blueprints and modules are paired randomly and without knowledge of that pairing during evolution.

The fitness value of the blueprints and modules is calculated after all genomes of the generation have been generated and evaluated. The fitness value of both blueprints and modules is the average fitness value of all genomes in which the respective blueprint or module was involved in.


Evolution
~~~~~~~~~

**[see CoDeepNEAT.evolve_population(...)]**

Evolving the CoDeepNEAT population can be divided into three major steps. First, the CoDeepNEAT population needs to be *selected*, which means that species and members of the population deemed fit enough to create offspring are selected while the rest of the population is erased. The second step is the actual evolution, during which the parental members of the generation are mutated and crossed over in order to create novel offspring with beneficial features. The third and last step during the evolution of a generation is the speciation of the population. The speciation clusters the members of the population in similar groups in order to identify traits and features, determine if those traits and features are beneficial and if applicable, facilitate the spread of those features or remove them from the population. The evolution of NEAT-like neuroevolution algorithms is guided through this speciation. TFNE currently supports three speciation methods for both modules and blueprints respectively, which are based on speciation methods from the original NEAT algorithm, though which have not been explicitely defined in the original research paper.

Since the different methods of speciation are very complex and take on an important role in NEAT-like neuroevolution algorithms is this specification of the CoDeepNEAT evolution subdivided into the specification of the actual mutation and crossover of the modules and blueprints as well as into the specification of the different speciation methods for them.


Module Mutation & Crossover
"""""""""""""""""""""""""""

The actual mutation and crossover phase for modules is very simple. As during the preceding selection phase all elligible parents for offspring have been determined and the number of offspring for each species has been calculated. New modules are created by conforming to those determined parameters and mutate / crossover the intendend amount of parents until the determined amount of offspring for each species has been reached. New modules are not automatically assigned the same species as their parents but are to be assigned to a species independently in the following speciation phase. In TFNE, if the ``mod_spec_reinit_extinct`` parameter has been set to true will the amount of modules belonging to species that went extinct in the preceding phase be reinitialized and treated as regular offspring that will be speciated in the following phase.

**Mutation** - Mutation for modules is the simple perturbation of the parameters of the parent module. The extent and manner in which this takes place is left up to the concrete implementation of module class. TFNE's pre-implemented modules perturb the parent module's parameters during mutation by selecting the offspring parameter from a normal distribution with the parent parameter value as the *mean* and the size of the standard distribution set via config. Mutating categorical parameters is done by randomly choosing a new value. TFNE also supports a config parameter (``mod_max_mutation``) that specifies the maximum degree in percent to which the parent parameters can be mutated.

**Crossover** - Crossover for modules is again left up to the concrete module class implementation. In TFNE pre-implemented modules, crossover is performed by averaging out the sortable parameters of both parent modules while categorical parameters are carried over from the fitter parent module.


Blueprint Mutation & Crossover
""""""""""""""""""""""""""""""

The mutation and crossover phase for blueprints is very similar to that of modules, with the exception of having different explicit mutation and crossover operations and an extra constraint regarding the extinction of module species. The first step of the mutation and crossover phase for blueprints is the check of all parental blueprints if their blueprint graphs contain references to module species (in the ``species`` value of the nodes) that are going extinct during this generation's evolution. If so, the parent's blueprint graph is mutated by replacing all references to extinct module species with references to randomly choosen non-extinct module species. The resulting mutated blueprint is then kept as a potential parent instead of the non-valid blueprint.

The rest of the mutation and crossover phase for blueprints is identical to that of modules. New offspring for each species is generated according to the predetermined amount. The type of mutation or crossover through which the offspring is generated is determined via percentage chance set via the config. Reinitialized blueprints will be generated if the ``bp_spec_reinit_extinct`` config parameter has been enabled. All generated offspring will be speciated in the following phase.

**Add Connection Mutation** - foobar

**Add Node Mutation** - foobar

**Remove Connection Mutation** - foobar

**Remove Node Mutation** - foobar

**Node Species Mutation** - foobar

**Optimizer Mutation** - foobar

**Crossover** - foobar


'basic' Module Speciation
"""""""""""""""""""""""""

foobar


'basic' Blueprint Speciation
""""""""""""""""""""""""""""

foobar


'param-distance-fixed' Module Speciation
""""""""""""""""""""""""""""""""""""""""

foobar


'gene-overlap-fixed' Blueprint Speciation
"""""""""""""""""""""""""""""""""""""""""

foobar


'param-distance-dynamic' Module Speciation
""""""""""""""""""""""""""""""""""""""""""

foobar


'gene-overlap-dynamic' Blueprint Speciation
"""""""""""""""""""""""""""""""""""""""""""

foobar

