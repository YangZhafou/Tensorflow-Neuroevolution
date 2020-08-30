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

+----------------------------------+-------------------------------------------+
| Blueprint genotype               | |bullet| Blueprint graph |br|             |
|                                  | |bullet| Optimizer configuration          |
+----------------------------------+-------------------------------------------+

A blueprint is the fundamental building block of a CoDeepNEAT genome, specifying the genome's basic ANN topology as well as all its hyperparameters that may be associated with that genome.

In TFNE the current extent of hyperparameters saved by blueprints is a full configuration of a Tensorflow optimizer, specifying all variables required for the training of the genome phenotype TF model. Additional hyperparameters such as possible training preprocessing operations can also be included, though are currently not part of TFNE's CoDeepNEAT. This Tensorflow optimizer configuration is the first part of the blueprint's genotype.

The second part of the blueprint genotype is the graph that is specifying the basic ANN topology. This graph will be referred to as the blueprint graph. The blueprint graph is a collection of node and connection *gene* instances. In TFNE, those node and connection gene classes are defined as listed below, demonstrating the extent of the information they contain. The purpose and functionality of these blueprint graph genes is very similar to the functionality of genome genes in the original NEAT algorithm [see `NEAT <../neat/neat-overview.html>`_], as they are adapted from those. The difference being that each node gene stores a module species and each connection gene merely indicates connections between nodes but not associated connection weights.

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

foobar


CoDeepNEAT Genome
~~~~~~~~~~~~~~~~~

foobar


--------------------------------------------------------------------------------

CoDeepNEAT Population
---------------------

foobar


--------------------------------------------------------------------------------

CoDeepNEAT Algorithm
--------------------

* Describe initialization, evaluation, evolution, etc in detail in their own
  SubSubHeadings.
* Go into detail about constraints and possible algorithmic details
* Include short references to variables


Initialization
~~~~~~~~~~~~~~

**[see CoDeepNEAT.initialize_population()]**

foobar


Evaluation
~~~~~~~~~~

**[see CoDeepNEAT.evaluate_population()]**

foobar


Evolution
~~~~~~~~~

**[see CoDeepNEAT.evolve_population()]**

foobar

