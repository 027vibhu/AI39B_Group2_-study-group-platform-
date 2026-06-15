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
=======
    def create_table(self):
        ensure_database_exists()
        self.execute(
            "CREATE TABLE IF NOT EXISTS exam_countdown ("
            "id INT AUTO_INCREMENT PRIMARY KEY,"
            "exam_name VARCHAR(120) NOT NULL DEFAULT 'Final Exams',"
            "exam_date DATETIME NOT NULL,"
            "is_active TINYINT(1) NOT NULL DEFAULT 1,"
            "created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
            "updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,"
            "INDEX idx_exam_countdown_active (is_active),"
            "INDEX idx_exam_countdown_date (exam_date)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
        )

    def get_active_exam(self):
        return self.fetch_one(
            "SELECT id, exam_name, exam_date, is_active, created_at, updated_at "
            "FROM exam_countdown WHERE is_active = 1 ORDER BY updated_at DESC LIMIT 1"
        )

    def save_active_exam(self, exam_name, exam_date):
        self.create_table()
        active_exam = self.get_active_exam()

        if active_exam:
            return self.execute(
                "UPDATE exam_countdown SET exam_name = %s, exam_date = %s, is_active = 1 WHERE id = %s",
                (exam_name, exam_date, active_exam['id']),
            )

        return self.execute(
            "INSERT INTO exam_countdown (exam_name, exam_date, is_active) VALUES (%s, %s, 1)",
            (exam_name, exam_date),
        )


_exam_countdown_model = ExamCountdownModel()


def create_exam_countdown_table():
    return _exam_countdown_model.create_table()


def get_active_exam():
    return _exam_countdown_model.get_active_exam()


def save_active_exam(exam_name, exam_date):
    return _exam_countdown_model.save_active_exam(exam_name, exam_date)
>>>>>>> origin/urbi
