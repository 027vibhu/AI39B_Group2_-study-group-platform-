import json
from app.models.base_model import BaseModel
from app.models.database import ensure_database_exists


class WhiteboardModel(BaseModel):
    @property
    def table(self):
        return 'whiteboard_state'

    def create_table(self):
        ensure_database_exists()
        create_query = (
            "CREATE TABLE IF NOT EXISTS whiteboard_state ("
            "id INT AUTO_INCREMENT PRIMARY KEY,"
            "room_id INT NOT NULL,"
            "state LONGTEXT NOT NULL,"
            "updated_by_user_id INT NULL,"
            "updated_by_username VARCHAR(50) NULL,"
            "updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,"
            "UNIQUE KEY uq_whiteboard_room (room_id),"
            "INDEX idx_whiteboard_room (room_id)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
        )
        return self.execute(create_query)

    def save_state(self, room_id, state_json, updated_by_user_id=None, updated_by_username=None):
        self.create_table()
        return self.execute(
            "INSERT INTO whiteboard_state (room_id, state, updated_by_user_id, updated_by_username) "
            "VALUES (%s, %s, %s, %s) "
            "ON DUPLICATE KEY UPDATE state = %s, updated_by_user_id = %s, updated_by_username = %s, updated_at = CURRENT_TIMESTAMP",
            (room_id, state_json, updated_by_user_id, updated_by_username, state_json, updated_by_user_id, updated_by_username),
        )

    def get_state(self, room_id):
        self.create_table()
        return self.fetch_one(
            "SELECT id, room_id, state, updated_by_user_id, updated_by_username, updated_at "
            "FROM whiteboard_state WHERE room_id = %s LIMIT 1",
            (room_id,),
        )

    def clear_state(self, room_id):
        self.create_table()
        return self.execute(
            "DELETE FROM whiteboard_state WHERE room_id = %s",
            (room_id,),
        )


_whiteboard_model = WhiteboardModel()


def create_whiteboard_table():
    return _whiteboard_model.create_table()


def save_whiteboard_state(room_id, state_json, updated_by_user_id=None, updated_by_username=None):
    return _whiteboard_model.save_state(room_id, state_json, updated_by_user_id, updated_by_username)


def get_whiteboard_state(room_id):
    return _whiteboard_model.get_state(room_id)


def clear_whiteboard_state(room_id):
    return _whiteboard_model.clear_state(room_id)
