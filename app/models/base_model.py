from app.models.database import ensure_database_exists, get_database_connection


class BaseModel:
    def __init__(self):
        ensure_database_exists()

    def get_connection(self):
        return get_database_connection()
