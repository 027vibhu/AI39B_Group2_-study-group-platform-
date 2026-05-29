from abc import ABC, abstractmethod

class BaseModel(ABC):
    """Abstract base model for all database models."""

    @classmethod
    @abstractmethod
    def ensure_table_exists(cls):
        raise NotImplementedError("Subclasses must implement ensure_table_exists")

    @classmethod
    @abstractmethod
    def get_database_connection(cls):
        raise NotImplementedError("Subclasses must implement get_database_connection")
