NEAT Overview
=============

**[WORK IN PROGRESS]**

The NeuroEvolution of Augmemting Topologies (NEAT) method was introduced in 2002 by Kenneth O. Stanley and Risto Miikkulainen and refined in 2 subsequent publications. These publications are listed below. NEATs basic idea is to start out with a minimal densely connected neural network and add a single or multiple neurons each generation, upon which each member of the population discerns itself more and more from the other members of the population. This allows the population to form clusters of similar population members, called species, that ideally each represent a different approach to the problem. This in turn then allows the algorithm to identify which approach to the problem works well and promote the further exploration of the according species.

Research papers that introduced the NEAT method:

* `Kenneth O. Stanley, Risto Miikkulainen - Evolving Neural Networks through Augmenting Topologies [2002] <http://nn.cs.utexas.edu/downloads/papers/stanley.ec02.pdf>`_
* `Kenneth O. Stanley, Risto Miikkulainen - Efficient Evolution of Neural Network Topologies [2002] <http://nn.cs.utexas.edu/downloads/papers/stanley.cec02.pdf>`_
* `Kenneth O. Stanley, Risto Miikkulainen - Efficient Evolution of Neural Networks through Complexification [2004] <http://nn.cs.utexas.edu/downloads/papers/stanley.phd04.pdf>`_


Genome Encoding
---------------

All information of a NEAT genotype is saved in the individual genes that make up the NEAT genome. The NEAT genome has no global parameters and its list of individual genes can be unordered.
There are three types of NEAT genes: A node gene, a connection gene and a bias gene. Each gene has a unique gene id.


NEAT Algorithm
--------------

Ipsum Lorem


SubSubHeading 1
~~~~~~~~~~~~~~~

this is an example text


SubSubHeading 2
~~~~~~~~~~~~~~~

that is continued here


Evolution of Bias Nodes
~~~~~~~~~~~~~~~~~~~~~~~

.. image:: ../illustrations/neat_bias_evolution.png


