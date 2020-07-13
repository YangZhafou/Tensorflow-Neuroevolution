from __future__ import annotations

from abc import ABCMeta, abstractmethod
import tensorflow as tf


class CoDeepNEATModuleBase(object, metaclass=ABCMeta):
    """"""

    def __init__(self, config_params, module_id, parent_mutation, dtype):
        self.config_params = config_params
        self.module_id = module_id
        self.parent_mutation = parent_mutation
        self.dtype = dtype
        self.fitness = 0

    @abstractmethod
    def __str__(self) -> str:
        """"""
        raise NotImplementedError("Subclass of CoDeepNEATModuleBase does not implement '__str__()'")

    @abstractmethod
    def initialize(self):
        """"""
        raise NotImplementedError("Subclass of CoDeepNEATModuleBase does not implement 'initialize()'")

    def set_fitness(self, fitness):
        self.fitness = fitness

    def get_id(self) -> int:
        return self.module_id

    def get_fitness(self) -> float:
        return self.fitness

    def get_merge_method(self) -> dict:
        return self.merge_method

    '''
    @abstractmethod
    def create_module_layers(self, dtype) -> [tf.keras.layers.Layer, ...]:
        """"""
        raise NotImplementedError("Subclass of CoDeepNEATModuleBase does not implement 'create_module_layers()'")

    @abstractmethod
    def create_downsampling_layer(self, in_shape, out_shape, dtype) -> tf.keras.layers.Layer:
        """"""
        raise NotImplementedError("Subclass of CoDeepNEATModuleBase does not implement 'create_downsampling_layer()'")

    @abstractmethod
    def create_mutation(self,
                        offspring_id,
                        max_degree_of_mutation) -> (int, CoDeepNEATModuleBase):
        """"""
        raise NotImplementedError("Subclass of CoDeepNEATModuleBase does not implement 'create_mutation()'")

    @abstractmethod
    def create_crossover(self,
                         offspring_id,
                         less_fit_module,
                         max_degree_of_mutation) -> (int, CoDeepNEATModuleBase):
        """"""
        raise NotImplementedError("Subclass of CoDeepNEATModuleBase does not implement 'create_crossover()'")

    @abstractmethod
    def serialize(self) -> dict:
        """"""
        raise NotImplementedError("Subclass of CoDeepNEATModuleBase does not implement 'serialize()'")

    @abstractmethod
    def get_distance(self, other_module) -> float:
        """"""
        raise NotImplementedError("Subclass of CoDeepNEATModuleBase does not implement 'get_distance()'")

    @abstractmethod
    def get_module_type(self) -> str:
        """"""
        raise NotImplementedError("Subclass of CoDeepNEATModuleBase does not implement 'get_module_name()'")
    '''
