import abc
from shared.cp import classproperty

class ObjectAction(abc.ABC):

    @classproperty
    @abc.abstractmethod
    def label(cls):
        raise NotImplementedError("Must override")

    @classmethod
    @abc.abstractmethod
    def executable(cls, entity):
        raise NotImplementedError("Must override")

    @classmethod
    @abc.abstractmethod
    def execute(cls, entity):
        raise NotImplementedError("Must override")