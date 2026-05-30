from app.models.database import get_database_connection


class BaseModel:
    """Base model providing raw SQL helpers using project's DB connection.

    Subclasses should use `execute`, `fetch_one`, and `fetch_all` for
    parameterized raw SQL queries.
    """

    def execute(self, query, params=None):
        connection = get_database_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params or ())
                # Return lastrowid if available, otherwise affected rowcount
                try:
                    return cursor.lastrowid or cursor.rowcount
                except Exception:
                    return cursor.rowcount
        finally:
            connection.close()

    def fetch_one(self, query, params=None):
        connection = get_database_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchone()
        finally:
            connection.close()

    def fetch_all(self, query, params=None):
        connection = get_database_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchall()
        finally:
            connection.close()
