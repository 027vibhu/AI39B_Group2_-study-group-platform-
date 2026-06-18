from app.models.base_model import BaseModel
from app.models.database import ensure_database_exists


class ExamCountdown(BaseModel):
    @property
    def table(self):
        return 'exam_countdown'

    @classmethod
    def ensure_table_exists(cls):
        ensure_database_exists()
        inst = cls()
        inst.execute(
            "CREATE TABLE IF NOT EXISTS exam_countdown ("
            "id INT AUTO_INCREMENT PRIMARY KEY,"
            "title VARCHAR(255) NOT NULL,"
            "exam_datetime DATETIME NOT NULL,"
            "notes TEXT NULL,"
            "color VARCHAR(20) NULL,"
            "user_id INT NOT NULL,"
            "created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
            "INDEX idx_exam_countdown_user (user_id),"
            "INDEX idx_exam_countdown_datetime (exam_datetime)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
        )


# module-level helpers for simple imports
_ec = ExamCountdown()


def ensure_table_exists():
    return ExamCountdown.ensure_table_exists()


def create_exam(title, exam_datetime, notes, user_id, color=None):
    """Insert a new exam countdown row and return its id."""
    _ec.ensure_table_exists()
    return _ec.execute(
        "INSERT INTO exam_countdown (title, exam_datetime, notes, color, user_id) "
        "VALUES (%s, %s, %s, %s, %s)",
        (title, exam_datetime, notes, color, user_id),
    )


def get_exams_for_user(user_id):
    _ec.ensure_table_exists()
    return _ec.fetch_all(
        "SELECT * FROM exam_countdown WHERE user_id = %s ORDER BY exam_datetime",
        (user_id,),
    )
