from app.models.base_model import BaseModel


class SharedFileModel(BaseModel):
    def create_table(self):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "CREATE TABLE IF NOT EXISTS shared_file ("
                    "id INT AUTO_INCREMENT PRIMARY KEY,"
                    "room_id INT NOT NULL,"
                    "user_id INT NOT NULL,"
                    "original_filename VARCHAR(255) NOT NULL,"
                    "stored_filename VARCHAR(255) NOT NULL,"
                    "file_path VARCHAR(500) NOT NULL,"
                    "mime_type VARCHAR(150) NOT NULL DEFAULT '',"
                    "size_bytes BIGINT NOT NULL DEFAULT 0,"
                    "uploaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
                    "INDEX idx_shared_file_room (room_id),"
                    "INDEX idx_shared_file_user (user_id)"
                    ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
                )
        finally:
            connection.close()
