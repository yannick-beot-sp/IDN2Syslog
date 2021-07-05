from __future__ import annotations
from abc import ABC, abstractmethod

class IStore(ABC):
    """
    Get and Set checkpoints
    """
    def __init__(self):
        pass

    @abstractmethod
    def set_parameter(self, name, value):
        pass

    @abstractmethod
    def get_parameter(self, name)-> str:
        pass