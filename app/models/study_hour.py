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

        db = Database()
        try:
            return db.fetch_all(
                "SELECT * FROM study_hours WHERE user_id = %s ORDER BY session_date DESC LIMIT %s",
                (user_id, limit),
            )
        finally:
            db.close()

    @classmethod
    def get_study_dates_for_user(cls, user_id: int, limit: int = 1000):
        """Return distinct study dates for a user, ordered ascending."""
        cls.ensure_table_exists()
        from app.models.database import Database

        db = Database()
        try:
            return db.fetch_all(
                "SELECT DISTINCT session_date FROM study_hours WHERE user_id = %s ORDER BY session_date ASC LIMIT %s",
                (user_id, limit),
            )
        finally:
            db.close()

    @classmethod
    def _calculate_current_streak(cls, study_dates):
        """Return the current active streak ending today or yesterday."""
        if not study_dates:
            return 0

        today = date.today()
        descending_dates = study_dates[::-1]
        last_date = descending_dates[0]
        days_since_last = (today - last_date).days

        # A streak is only active if the most recent study day is today or yesterday.
        if days_since_last > 1:
            return 0

        current_streak = 1
        previous = last_date
        for current_date in descending_dates[1:]:
            diff = (previous - current_date).days
            if diff == 1:
                current_streak += 1
                previous = current_date
            elif diff == 0:
                continue
            else:
                break

        return current_streak

    @classmethod
    def get_study_streaks(cls, user_id: int):
        """Calculate current and longest consecutive study day streaks."""
        date_rows = cls.get_study_dates_for_user(user_id)
        if not date_rows:
            return {
                'current_streak': 0,
                'longest_streak': 0,
                'last_study_date': None,
                'streak_active': False,
            }

        study_dates = [row['session_date'] for row in date_rows]
        longest = 1
        consecutive = 1
        previous_date = study_dates[0]

        for current_date in study_dates[1:]:
            diff = (current_date - previous_date).days
            if diff == 1:
                consecutive += 1
            elif diff == 0:
                # same date may appear more than once in source data; ignore duplicates.
                pass
            else:
                longest = max(longest, consecutive)
                consecutive = 1
            previous_date = current_date

        longest = max(longest, consecutive)

        current_streak = cls._calculate_current_streak(study_dates)
        last_study_date = study_dates[-1]
        streak_active = current_streak > 0

        return {
            'current_streak': current_streak,
            'longest_streak': longest,
            'last_study_date': last_study_date,
            'streak_active': streak_active,
        }
