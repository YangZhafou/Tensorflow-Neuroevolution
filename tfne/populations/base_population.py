from abc import ABCMeta, abstractmethod

from ..encodings.base_genome import BaseGenome


class BasePopulation(object, metaclass=ABCMeta):
    """"""

    @abstractmethod
    def get_best_genome(self) -> BaseGenome:
        """"""
        raise NotImplementedError("Subclass of BasePopulation does not implement 'get_best_genome()'")

    @abstractmethod
    def save_population(self, save_dir_path):
        """"""
        raise NotImplementedError("Subclass of BasePopulation does not implement 'save_population()'")
