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

foobar


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

