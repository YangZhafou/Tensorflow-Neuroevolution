from typing import Union, Any
from abc import ABCMeta, abstractmethod

import tensorflow as tf


class BaseGenome(object, metaclass=ABCMeta):
    """"""

    @abstractmethod
    def __call__(self, inputs) -> tf.Tensor:
        """"""
        raise NotImplementedError("Subclass of BaseGenome does not implement '__call__()'")

    @abstractmethod
    def __str__(self) -> str:
        """"""
        raise NotImplementedError("Subclass of BaseGenome does not implement '__str__()'")

    @abstractmethod
    def visualize(self, show, save_dir_path, **kwargs) -> str:
        """"""
        raise NotImplementedError("Subclass of BaseGenome does not implement 'visualize()'")

    @abstractmethod
    def serialize(self) -> dict:
        """"""
        raise NotImplementedError("Subclass of BaseGenome does not implement 'serialize()'")

    @abstractmethod
    def save_genotype(self, save_dir_path) -> str:
        """"""
        raise NotImplementedError("Subclass of BaseGenome does not implement 'save_genotype()'")

    @abstractmethod
    def save_model(self, file_path, **kwargs):
        """"""
        raise NotImplementedError("Subclass of BaseGenome does not implement 'save_model()'")

    @abstractmethod
    def set_fitness(self, fitness):
        """"""
        raise NotImplementedError("Subclass of BaseGenome does not implement 'set_fitness()'")

    @abstractmethod
    def get_genotype(self) -> Any:
        """"""
        raise NotImplementedError("Subclass of BaseGenome does not implement 'get_genotype()'")

    @abstractmethod
    def get_model(self) -> tf.keras.Model:
        """"""
        raise NotImplementedError("Subclass of BaseGenome does not implement 'get_model()'")

    @abstractmethod
    def get_optimizer(self) -> Union[None, tf.keras.optimizers.Optimizer]:
        """"""
        raise NotImplementedError("Subclass of BaseGenome does not implement 'get_optimizer()'")

    @abstractmethod
    def get_id(self) -> int:
        """"""
        raise NotImplementedError("Subclass of BaseGenome does not implement 'get_id()'")

    @abstractmethod
    def get_fitness(self) -> float:
        """"""
        raise NotImplementedError("Subclass of BaseGenome does not implement 'get_fitness()'")
