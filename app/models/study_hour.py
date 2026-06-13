from app.models.base_model import BaseModel
from app.models.database import Database, ensure_database_exists


class StudyHour(BaseModel):
    @property
    def table(self):
        return 'study_hours'

    @staticmethod
    def create_study_hours_table():
        ensure_database_exists()
        db = Database()
        try:
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS study_hours (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    study_date DATE NOT NULL,
                    duration_minutes INT NOT NULL,
                    subject VARCHAR(255) NULL,
                    notes TEXT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_study_hours_user_id (user_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )
        finally:
            db.close()

    def log_study_hours(self, user_id, study_date, duration_minutes, subject=None, notes=None):
        return self.execute(
            "INSERT INTO study_hours (user_id, study_date, duration_minutes, subject, notes) VALUES (%s, %s, %s, %s, %s)",
            (user_id, study_date, duration_minutes, subject, notes),
        )

    def get_study_hours_for_user(self, user_id):
        return self.fetch_all(
            "SELECT * FROM study_hours WHERE user_id = %s ORDER BY study_date DESC, created_at DESC",
            (user_id,),
        )

    def get_total_minutes_for_user(self, user_id):
        result = self.fetch_one(
            "SELECT COALESCE(SUM(duration_minutes), 0) AS total_minutes FROM study_hours WHERE user_id = %s",
            (user_id,),
        )
        return result['total_minutes'] if result else 0

    def get_current_streak(self, user_id):
        # This is a simplified streak calculation: counts consecutive days with at least 1 study session,
        # looking back from today.
        query = """
            SELECT study_date
            FROM study_hours
            WHERE user_id = %s
            GROUP BY study_date
            ORDER BY study_date DESC
        """
        dates = self.fetch_all(query, (user_id,))
        if not dates:
            return 0
        
        streak = 0
        from datetime import date, timedelta
        
        check_date = date.today()
        # If they studied today, start counting, otherwise check yesterday
        # This implementation counts consecutive days up to today.
        
        study_dates = {d['study_date'] for d in dates}
        
        current_streak = 0
        d = date.today()
        while d in study_dates or d == date.today(): # Allow streak if studied today or yesterday
             if d in study_dates:
                 current_streak += 1
             elif d < date.today(): # If they didn't study yesterday, streak broken
                 break
             d -= timedelta(days=1)
             
        return current_streak
