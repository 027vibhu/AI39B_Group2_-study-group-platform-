from app.models.base_model import BaseModel
from app.models.database import Database, ensure_database_exists


class Note(BaseModel):
    @property
    def table(self):
        return 'notes'

    @staticmethod
    def create_notes_table():
        ensure_database_exists()
        db = Database()
        try:
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS notes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    pdf_url VARCHAR(255) NOT NULL,
                    description TEXT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_notes_user_id (user_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )
        finally:
            db.close()

    def create_note(self, user_id, title, pdf_url, description=None):
        return self.execute(
            "INSERT INTO notes (user_id, title, pdf_url, description) VALUES (%s, %s, %s, %s)",
            (user_id, title, pdf_url, description),
        )

    def get_notes_for_user(self, user_id):
        return self.fetch_all(
            "SELECT * FROM notes WHERE user_id = %s ORDER BY created_at DESC",
            (user_id,),
        )

    def get_note_by_id(self, note_id):
        return self.find_by_id(note_id)
