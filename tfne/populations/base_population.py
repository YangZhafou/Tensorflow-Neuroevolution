from abc import ABCMeta, abstractmethod


class BasePopulation(object, metaclass=ABCMeta):
    """"""

    @abstractmethod
    def serialize(self) -> dict:
        """"""
        raise NotImplementedError("Subclass of BasePopulation does not implement 'serialize()'")
