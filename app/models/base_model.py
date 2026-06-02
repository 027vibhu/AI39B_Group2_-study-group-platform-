<<<<<<< HEAD
class BaseModel:
    """Base model class for shared model behavior."""

    def __init__(self):
        pass
=======
from abc import ABC, abstractmethod




class BaseModel(ABC):
    """Abstract base model with convenience helpers for simple tables.

    Subclasses should define a `table` property and can use the provided
    helpers (`find_by_id`, `find_by`, `find_all`, `count_all`) to interact
    with the database without writing boilerplate each time.
    """

    @property
    @abstractmethod
    def table(self):
        raise NotImplementedError()

    def find_by_id(self, id_):
        from app.models.database import Database
        db = Database()
        try:
            r = db.fetch_one(f"SELECT * FROM {self.table} WHERE id = %s", (id_,))
            return r
        finally:
            db.close()

    def find_by(self, column, value):
        from app.models.database import Database
        db = Database()
        try:
            r = db.fetch_one(f"SELECT * FROM {self.table} WHERE {column} = %s", (value,))
            return r
        finally:
            db.close()

    def find_all(self, order_by='id'):
        from app.models.database import Database
        db = Database()
        try:
            r = db.fetch_all(f"SELECT * FROM {self.table} ORDER BY {order_by}")
            return r
        finally:
            db.close()

    def count_all(self):
        from app.models.database import Database
        db = Database()
        try:
            r = db.fetch_one(f"SELECT COUNT(*) AS total FROM {self.table}")
            return r['total'] if r else 0
        finally:
            db.close()

    # Convenience passthroughs used by some legacy models
    def execute(self, query: str, params=None):
        from app.models.database import Database
        db = Database()
        try:
            return db.execute(query, params)
        finally:
            db.close()

    def fetch_one(self, query: str, params=None):
        from app.models.database import Database
        db = Database()
        try:
            return db.fetch_one(query, params)
        finally:
            db.close()

    def fetch_all(self, query: str, params=None):
        from app.models.database import Database
        db = Database()
        try:
            return db.fetch_all(query, params)
        finally:
            db.close()
>>>>>>> 60ab2a74498b01c2f9451141b9df7fa3c555ab46
