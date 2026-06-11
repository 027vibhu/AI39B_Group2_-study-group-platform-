from app.models.base_model import BaseModel
from app.models.database import ensure_database_exists


class ExamCountdownModel(BaseModel):
    @property
    def table(self):
        return 'exam_countdown'

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