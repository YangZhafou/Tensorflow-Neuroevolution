from abc import ABCMeta, abstractmethod


class BasePopulation(object, metaclass=ABCMeta):
    """"""

    @abstractmethod
    def save_population(self, save_dir_path):
        """"""
        raise NotImplementedError("Subclass of BasePopulation does not implement 'save_population()'")
