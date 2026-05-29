from app.models.base_model import BaseModel


class RoomModel(BaseModel):
    """Model for room-related DB operations using raw SQL.

    Provides methods to create the `room` table and fetch all public rooms (is_private = 0).
    """

    def create_table(self):
        """Create the `room` table if it does not exist."""
        query = (
            "CREATE TABLE IF NOT EXISTS room ("
            "id INT AUTO_INCREMENT PRIMARY KEY,"
            "code VARCHAR(6) NOT NULL UNIQUE,"
            "name VARCHAR(120) NOT NULL DEFAULT '',"
            "is_private TINYINT(1) NOT NULL DEFAULT 0,"
            "created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
        )
        return self.execute(query)

    def get_all_public_rooms(self):
        query = (
            "SELECT id, code, name, is_private, created_at "
            "FROM room WHERE is_private = 0 "
            "ORDER BY created_at DESC"
        )
        return self.fetch_all(query)
