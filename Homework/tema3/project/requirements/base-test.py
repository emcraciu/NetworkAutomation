from abc import ABC, abstractmethod

class TestInterface(ABC):

    @abstractmethod
    def run(self):
        pass