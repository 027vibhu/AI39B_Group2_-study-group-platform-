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
                CREATE TABLE IF NOT EXISTS flashcard_sets (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    note_id INT NOT NULL,
                    user_id INT NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    card_count INT NOT NULL DEFAULT 0,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_flashcard_sets_note (note_id),
                    INDEX idx_flashcard_sets_user (user_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS flashcards (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    set_id INT NULL,
                    note_id INT NOT NULL,
                    user_id INT NOT NULL,
                    question VARCHAR(500) NOT NULL,
                    answer TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_flashcards_note (note_id),
                    INDEX idx_flashcards_user (user_id),
                    INDEX idx_flashcards_set (set_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )
            # Best-effort: add set_id to pre-existing flashcards tables.
            try:
                db.execute("ALTER TABLE flashcards ADD COLUMN set_id INT NULL AFTER id")
            except Exception:
                pass
            try:
                db.execute("ALTER TABLE flashcards ADD INDEX idx_flashcards_set (set_id)")
            except Exception:
                pass
        finally:
            db.close()

    def create_set(self, note_id, user_id, title, card_count):
        return self.execute(
            "INSERT INTO flashcard_sets (note_id, user_id, title, card_count) VALUES (%s, %s, %s, %s)",
            (note_id, user_id, title, card_count),
        )

    def get_sets_for_note(self, note_id):
        return self.fetch_all(
            "SELECT * FROM flashcard_sets WHERE note_id = %s ORDER BY created_at DESC, id DESC",
            (note_id,),
        )

    def get_set_by_id(self, set_id):
        return self.fetch_one(
            "SELECT * FROM flashcard_sets WHERE id = %s",
            (set_id,),
        )

    def create_flashcard(self, note_id, user_id, question, answer, set_id=None):
        return self.execute(
            "INSERT INTO flashcards (set_id, note_id, user_id, question, answer) VALUES (%s, %s, %s, %s, %s)",
            (set_id, note_id, user_id, question, answer),
        )

    def get_flashcards_for_set(self, set_id):
        return self.fetch_all(
            "SELECT * FROM flashcards WHERE set_id = %s ORDER BY id ASC",
            (set_id,),
        )

    def get_flashcards_for_note(self, note_id):
        return self.fetch_all(
            "SELECT * FROM flashcards WHERE note_id = %s ORDER BY id ASC",
            (note_id,),
        )

    def count_for_note(self, note_id):
        row = self.fetch_one(
            "SELECT COUNT(*) AS total FROM flashcards WHERE note_id = %s",
            (note_id,),
        )
        return row['total'] if row else 0

    def delete_flashcards_for_note(self, note_id):
        self.execute("DELETE FROM flashcard_sets WHERE note_id = %s", (note_id,))
        return self.execute(
            "DELETE FROM flashcards WHERE note_id = %s",
            (note_id,),
        )
