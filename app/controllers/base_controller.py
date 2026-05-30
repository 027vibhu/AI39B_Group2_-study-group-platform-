from abc import ABC, abstractmethod

class BaseController(ABC):
    """Abstract base controller for handling request logic."""

    def __init__(self):
        pass

    @abstractmethod
    def handle(self, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement handle")
