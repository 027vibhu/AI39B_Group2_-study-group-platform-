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

    @staticmethod
    def create_note_shares_table():
        ensure_database_exists()
        db = Database()
        try:
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS note_shares (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    note_id INT NOT NULL,
                    shared_with_user_id INT NOT NULL,
                    shared_by_user_id INT NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY uq_note_share (note_id, shared_with_user_id),
                    INDEX idx_note_shares_recipient (shared_with_user_id)
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

    def get_all_notes(self):
        return self.fetch_all(
            "SELECT n.*, u.username AS owner_username "
            "FROM notes n LEFT JOIN users u ON u.id = n.user_id "
            "ORDER BY n.created_at DESC"
        )

    def get_note_by_id(self, note_id):
        return self.find_by_id(note_id)

    def share_note(self, note_id, shared_with_user_id, shared_by_user_id):
        return self.execute(
            "INSERT IGNORE INTO note_shares (note_id, shared_with_user_id, shared_by_user_id) "
            "VALUES (%s, %s, %s)",
            (note_id, shared_with_user_id, shared_by_user_id),
        )

    def delete_note(self, note_id):
        self.execute("DELETE FROM note_shares WHERE note_id = %s", (note_id,))
        return self.execute("DELETE FROM notes WHERE id = %s", (note_id,))

    def get_shared_notes_for_user(self, user_id):
        return self.fetch_all(
            "SELECT n.*, u.username AS shared_by "
            "FROM note_shares s "
            "JOIN notes n ON n.id = s.note_id "
            "JOIN users u ON u.id = s.shared_by_user_id "
            "WHERE s.shared_with_user_id = %s "
            "ORDER BY s.created_at DESC",
            (user_id,),
        )
