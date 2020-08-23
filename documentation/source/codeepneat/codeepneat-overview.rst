CoDeepNEAT Overview
===================

The Coevolution Deep NeuroEvolution of Augmemting Topologies (CoDeepNEAT) method was first introduced in 2017 by a Team of researchers from Sentient Technologies and the University of Texas at Austin. CoDeepNEAT is a layer evolving algorithm that aims to exploit repetitive structure in the problem domain. It does so by splitting the genome into two elements that can be combined to form a genome, though which each have their own population that is evolved seperately according to the methods of neuroevolution. The two elements that make up a genome are termed the blueprint and the modules. A module is a small deep neural network of predefined complexity and configuration that is intended to represent one instance of the repetitive structure of the problem domain. Those modules are concatenated in an overarching graph, that is the blueprint. This blueprint graph is very similar to the genome graph employed by DeepNEAT though instead of nodes representing layers do the nodes of the blueprint graph represent modules, whereas a single module is often repeated multiple times in a blueprint graph. This neuroevolution method therefore aims to evolve neural network with repetitive topologies to effectively exploit repetitive structure in the problem domain.

Research paper that introduced the CoDeepNEAT method:

* `Evolving Deep Neural Networks [2017] <https://arxiv.org/abs/1703.00548>`_


--------------------------------------------------------------------------------

Subheading 1
------------

foobar


SubSubHeading 1
~~~~~~~~~~~~~~~

foobar

