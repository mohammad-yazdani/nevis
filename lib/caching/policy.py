from abc import ABC, abstractmethod


class Policy(ABC):

    def __init__(self, window_size):
        self.wsz = window_size

    @abstractmethod
    def resolve(self, key):
        pass

    @abstractmethod
    def evict(self):
        pass
