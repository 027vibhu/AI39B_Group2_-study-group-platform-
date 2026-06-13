from app.models.base_model import BaseModel
from app.models.database import ensure_database_exists


class StudyStreakModel(BaseModel):
    @property
    def table(self):
        return 'study_streaks'

    def create_table(self):
        ensure_database_exists()
        return self.execute(
            "CREATE TABLE IF NOT EXISTS study_streaks ("
            "id INT AUTO_INCREMENT PRIMARY KEY,"
            "user_id INT NOT NULL," 
            "current_streak INT NOT NULL DEFAULT 0,"
            "longest_streak INT NOT NULL DEFAULT 0,"
            "last_study_date DATE NULL," 
            "updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,"
            "created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP," 
            "UNIQUE KEY uq_study_streak_user (user_id),"
            "INDEX idx_study_streak_user (user_id)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
        )

    def get_streak_by_user(self, user_id):
        self.create_table()
        return self.fetch_one(
            "SELECT id, user_id, current_streak, longest_streak, last_study_date, updated_at, created_at "
            "FROM study_streaks WHERE user_id = %s LIMIT 1",
            (user_id,),
        )

    def upsert_study_streak(self, user_id, current_streak, longest_streak, last_study_date):
        self.create_table()
        return self.execute(
            "INSERT INTO study_streaks (user_id, current_streak, longest_streak, last_study_date) "
            "VALUES (%s, %s, %s, %s) "
            "ON DUPLICATE KEY UPDATE current_streak = VALUES(current_streak), "
            "longest_streak = VALUES(longest_streak), last_study_date = VALUES(last_study_date), "
            "updated_at = CURRENT_TIMESTAMP",
            (user_id, current_streak, longest_streak, last_study_date),
        )


_study_streak_model = StudyStreakModel()


def create_study_streaks_table():
    return _study_streak_model.create_table()


def get_study_streak_by_user(user_id):
    return _study_streak_model.get_streak_by_user(user_id)


def upsert_study_streak(user_id, current_streak, longest_streak, last_study_date):
    return _study_streak_model.upsert_study_streak(user_id, current_streak, longest_streak, last_study_date)
