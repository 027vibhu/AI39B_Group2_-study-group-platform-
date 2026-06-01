from app.models.base_model import BaseModel
from app.models.database import ensure_database_exists
from datetime import datetime, timedelta


class RoomModel(BaseModel):
    @property
    def table(self):
        return 'room'

    def create_table(self):
        ensure_database_exists()
        create_query = (
            "CREATE TABLE IF NOT EXISTS room ("
            "id INT AUTO_INCREMENT PRIMARY KEY,"
            "code VARCHAR(6) NOT NULL UNIQUE,"
            "name VARCHAR(120) NOT NULL DEFAULT '',"
            "is_private TINYINT(1) NOT NULL DEFAULT 0,"
            "subject_tags VARCHAR(255) DEFAULT '',"
            "created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
        )
        self.execute(create_query)

    def create_user_rooms_table(self):
        ensure_database_exists()
        return self.execute(
            "CREATE TABLE IF NOT EXISTS user_room ("
            "id INT AUTO_INCREMENT PRIMARY KEY,"
            "user_id INT NOT NULL,"
            "room_id INT NOT NULL,"
            "created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
            "UNIQUE KEY uq_user_room (user_id, room_id),"
            "INDEX idx_user_room_user (user_id),"
            "INDEX idx_user_room_room (room_id)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
        )

    def get_room_by_code(self, room_code):
        return self.fetch_one(
            "SELECT id, code, name, is_private, subject_tags, created_at FROM room WHERE code = %s LIMIT 1",
            (room_code,),
        )

    def get_room_by_id(self, room_id):
        return self.fetch_one(
            "SELECT id, code, name, is_private, subject_tags, created_at FROM room WHERE id = %s LIMIT 1",
            (room_id,),
        )

    def create_room(self, code, name, is_private, subject_tags):
        self.create_table()
        rid = self.execute(
            "INSERT INTO room (code, name, is_private, subject_tags) VALUES (%s, %s, %s, %s)",
            (code, name, int(is_private), subject_tags),
        )
        # execute returns lastrowid for inserts
        return self.get_room_by_id(rid)

    def create_user_room(self, user_id, room_id):
        self.create_user_rooms_table()
        return self.execute(
            "INSERT INTO user_room (user_id, room_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE id = id",
            (user_id, room_id),
        )

    def is_user_in_room(self, user_id, room_id):
        return bool(self.fetch_one("SELECT 1 FROM user_room WHERE user_id = %s AND room_id = %s LIMIT 1", (user_id, room_id)))

    def get_joined_rooms_for_user(self, user_id, limit=8):
        return self.fetch_all(
            "SELECT room.id, room.code, room.name, room.is_private, room.subject_tags, room.created_at "
            "FROM user_room JOIN room ON room.id = user_room.room_id "
            "WHERE user_room.user_id = %s ORDER BY user_room.created_at DESC LIMIT %s",
            (user_id, limit),
        )

    def get_all_public_rooms(self):
        return self.fetch_all(
            "SELECT id, code, name, is_private, created_at FROM room WHERE is_private = 0 ORDER BY created_at DESC"
        )

    def delete_room_by_id(self, room_id):
        self.execute("DELETE FROM message WHERE room_id = %s", (room_id,))
        self.execute("DELETE FROM user_room WHERE room_id = %s", (room_id,))
        return self.execute("DELETE FROM room WHERE id = %s", (room_id,))

    def delete_room_by_code(self, room_code):
        room = self.get_room_by_code(room_code)
        if not room:
            return 0
        return self.delete_room_by_id(room['id'])

    def log_room_action(self, username, room_name, action_type, duration_minutes=None, reason=None):
        ban_until = None
        if action_type == 'ban' and duration_minutes:
            ban_until = datetime.now() + timedelta(minutes=int(duration_minutes))
        return self.execute(
            "INSERT INTO room_actions (username, room_name, action_type, ban_until, reason) VALUES (%s, %s, %s, %s, %s)",
            (username, room_name, action_type, ban_until, reason),
        )

    def is_user_banned_from_room(self, username, room_name):
        row = self.fetch_one(
            "SELECT * FROM room_actions WHERE username = %s AND room_name = %s AND action_type = 'ban' "
            "AND (ban_until IS NULL OR ban_until > NOW()) ORDER BY created_at DESC LIMIT 1",
            (username, room_name),
        )
        return row is not None


# module-level compatibility
_room_model = RoomModel()


def create_rooms_table():
    return _room_model.create_table()


def create_user_rooms_table():
    return _room_model.create_user_rooms_table()


def get_room_by_code(room_code):
    return _room_model.get_room_by_code(room_code)


def get_room_by_id(room_id):
    return _room_model.get_room_by_id(room_id)


def create_room(code, name, is_private, subject_tags):
    return _room_model.create_room(code, name, is_private, subject_tags)


def create_user_room(user_id, room_id):
    return _room_model.create_user_room(user_id, room_id)


def is_user_in_room(user_id, room_id):
    return _room_model.is_user_in_room(user_id, room_id)


def get_joined_rooms_for_user(user_id, limit=8):
    return _room_model.get_joined_rooms_for_user(user_id, limit)


def get_all_public_rooms():
    return _room_model.get_all_public_rooms()


def delete_room_by_id(room_id):
    return _room_model.delete_room_by_id(room_id)


def delete_room_by_code(room_code):
    return _room_model.delete_room_by_code(room_code)


def log_room_action(username, room_name, action_type, duration_minutes=None, reason=None):
    return _room_model.log_room_action(username, room_name, action_type, duration_minutes, reason)


def is_user_banned_from_room(username, room_name):
    return _room_model.is_user_banned_from_room(username, room_name)
