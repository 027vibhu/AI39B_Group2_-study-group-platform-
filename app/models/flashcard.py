from app.models.base_model import BaseModel
from app.models.database import Database, ensure_database_exists


class Flashcard(BaseModel):
    @property
    def table(self):
        return 'flashcards'

    @staticmethod
    def create_flashcards_table():
        ensure_database_exists()
        db = Database()
        try:
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS flashcards (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    note_id INT NOT NULL,
                    user_id INT NOT NULL,
                    front_text TEXT NOT NULL,
                    back_text TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_flashcards_note_id (note_id),
                    INDEX idx_flashcards_user_id (user_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )
        finally:
            db.close()

    def create_flashcard(self, note_id, user_id, front_text, back_text):
        return self.execute(
            "INSERT INTO flashcards (note_id, user_id, front_text, back_text) VALUES (%s, %s, %s, %s)",
            (note_id, user_id, front_text, back_text),
        )

    def get_flashcards_for_note(self, note_id, user_id):
        return self.fetch_all(
            "SELECT * FROM flashcards WHERE note_id = %s AND user_id = %s ORDER BY created_at DESC",
            (note_id, user_id),
        )

    def get_flashcard_by_id(self, flashcard_id):
        return self.find_by_id(flashcard_id)

    def delete_flashcard(self, flashcard_id, user_id):
        return self.execute(
            "DELETE FROM flashcards WHERE id = %s AND user_id = %s",
            (flashcard_id, user_id),
        )

    def get_flashcards_for_user(self, user_id):
        return self.fetch_all(
            "SELECT * FROM flashcards WHERE user_id = %s ORDER BY created_at DESC",
            (user_id,),
        )
