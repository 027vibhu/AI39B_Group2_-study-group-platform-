from datetime import date

from app.models.base_model import BaseModel


def create_study_hours_table():
    """Create the study_hours table if it does not exist."""
    # Use the existing helpers from database.py to ensure DB exists and open a connection
    from app.models.database import ensure_database_exists, get_database_connection

    ensure_database_exists()
    connection = get_database_connection()
    try:
        with connection.cursor() as cursor:
            sql = (
                "CREATE TABLE IF NOT EXISTS study_hours ("
                "id INT AUTO_INCREMENT PRIMARY KEY,"
                "user_id INT NOT NULL,"
                "session_date DATE NOT NULL,"
                "duration_minutes INT NOT NULL,"
                "notes TEXT NULL,"
                "created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"
                ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
            )
            cursor.execute(sql)
            # Add helpful indexes if they don't exist (ignore failures)
            try:
                cursor.execute("ALTER TABLE study_hours ADD INDEX idx_study_hours_user_id (user_id)")
            except Exception:
                pass
            try:
                cursor.execute("ALTER TABLE study_hours ADD INDEX idx_study_hours_date (session_date)")
            except Exception:
                pass
    finally:
        connection.close()


class StudyHour(BaseModel):

    """Model for tracking study sessions.

    This model uses raw SQL for all database interactions and provides a
    helper to ensure its table exists before writes/reads.
    """

    @property
    def table(self):
        return 'study_hours'

    @classmethod
    def ensure_table_exists(cls):
        create_study_hours_table()

    @classmethod
    def record(cls, user_id: int, session_date: date, duration_minutes: int, notes: str = None):
        """Insert a study session record and return the new row id."""
        cls.ensure_table_exists()
        from app.models.database import Database

        db = Database()
        try:
            return db.execute(
                "INSERT INTO study_hours (user_id, session_date, duration_minutes, notes) VALUES (%s, %s, %s, %s)",
                (user_id, session_date, duration_minutes, notes),
            )
        finally:
            db.close()

    @classmethod
    def find_for_user(cls, user_id: int, limit: int = 50):
        """Return recent study sessions for a user."""
        cls.ensure_table_exists()
        from app.models.database import Database
# Note: The above functions are simple wrappers around the StudyHour class methods, and can be used directly in the application code.
        db = Database()
        try:
            return db.fetch_all(
                "SELECT * FROM study_hours WHERE user_id = %s ORDER BY session_date DESC LIMIT %s",
                (user_id, limit),
            )
        finally:
            db.close()
