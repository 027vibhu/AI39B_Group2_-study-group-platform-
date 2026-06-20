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
            "owner_id INT NULL,"
            "code VARCHAR(6) NOT NULL UNIQUE,"
            "name VARCHAR(120) NOT NULL DEFAULT '',"
            "is_private TINYINT(1) NOT NULL DEFAULT 0,"
            "subject_tags VARCHAR(255) DEFAULT '',"
            "created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
        )
        self.execute(create_query)
        # Best-effort: add columns on existing tables
        try:
            self.execute("ALTER TABLE room ADD COLUMN owner_id INT NULL AFTER id")
        except Exception:
            pass
        try:
            self.execute("ALTER TABLE room ADD COLUMN subject_tags VARCHAR(255) DEFAULT '' AFTER is_private")
        except Exception:
            pass

    def create_user_rooms_table(self):
        ensure_database_exists()
        result = self.execute(
            "CREATE TABLE IF NOT EXISTS user_room ("
            "id INT AUTO_INCREMENT PRIMARY KEY,"
            "user_id INT NOT NULL,"
            "room_id INT NOT NULL,"
            "role VARCHAR(20) NOT NULL DEFAULT 'member',"
            "created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
            "UNIQUE KEY uq_user_room (user_id, room_id),"
            "INDEX idx_user_room_user (user_id),"
            "INDEX idx_user_room_room (room_id)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
        )
        # Best-effort: add the role column on pre-existing tables
        try:
            self.execute("ALTER TABLE user_room ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'member' AFTER room_id")
        except Exception:
            pass
        return result

    def create_moderation_log_table(self):
        ensure_database_exists()
        return self.execute(
            "CREATE TABLE IF NOT EXISTS room_moderation_log ("
            "id INT AUTO_INCREMENT PRIMARY KEY,"
            "room_id INT NULL,"
            "room_code VARCHAR(6) NOT NULL,"
            "actor_user_id INT NULL,"
            "actor_username VARCHAR(50) NOT NULL,"
            "target_username VARCHAR(50) NOT NULL,"
            "action_type ENUM('kick', 'ban') NOT NULL,"
            "duration_minutes INT NULL,"
            "reason TEXT NULL,"
            "created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
            "INDEX idx_room_moderation_room_code (room_code),"
            "INDEX idx_room_moderation_room_id (room_id),"
            "INDEX idx_room_moderation_target (target_username)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
        )

    def get_room_by_code(self, room_code):
        return self.fetch_one(
            "SELECT id, owner_id, code, name, is_private, subject_tags, created_at FROM room WHERE code = %s LIMIT 1",
            (room_code,),
        )

    def get_room_by_id(self, room_id):
        return self.fetch_one(
            "SELECT id, owner_id, code, name, is_private, subject_tags, created_at FROM room WHERE id = %s LIMIT 1",
            (room_id,),
        )

    def create_room(self, code, name, is_private, subject_tags, owner_id=None):
        self.create_table()
        rid = self.execute(
            "INSERT INTO room (code, name, is_private, subject_tags, owner_id) VALUES (%s, %s, %s, %s, %s)",
            (code, name, int(is_private), subject_tags, owner_id),
        )
        # Record the creator as the room owner in the membership table
        if owner_id:
            self.create_user_room(owner_id, rid, role='owner')
        # execute returns lastrowid for inserts
        return self.get_room_by_id(rid)

    def create_user_room(self, user_id, room_id, role='member'):
        self.create_user_rooms_table()
        # Insert membership; keep the existing role if the row already exists
        return self.execute(
            "INSERT INTO user_room (user_id, room_id, role) VALUES (%s, %s, %s) "
            "ON DUPLICATE KEY UPDATE role = role",
            (user_id, room_id, role),
        )

    def is_user_in_room(self, user_id, room_id):
        return bool(self.fetch_one("SELECT 1 FROM user_room WHERE user_id = %s AND room_id = %s LIMIT 1", (user_id, room_id)))

    def set_user_room_role(self, user_id, room_id, role):
        self.create_user_rooms_table()
        # Ensure a membership row exists, then set the role
        self.create_user_room(user_id, room_id)
        return self.execute(
            "UPDATE user_room SET role = %s WHERE user_id = %s AND room_id = %s",
            (role, user_id, room_id),
        )

    def get_user_room_role(self, user_id, room_id):
        row = self.fetch_one(
            "SELECT role FROM user_room WHERE user_id = %s AND room_id = %s LIMIT 1",
            (user_id, room_id),
        )
        return row['role'] if row else None

    def get_room_members_with_roles(self, room_id):
        return self.fetch_all(
            "SELECT ur.user_id, u.username, ur.role "
            "FROM user_room ur JOIN users u ON u.id = ur.user_id "
            "WHERE ur.room_id = %s "
            "ORDER BY FIELD(ur.role, 'owner', 'moderator', 'member'), u.username ASC",
            (room_id,),
        )

    def get_joined_rooms_for_user(self, user_id, limit=8):
        return self.fetch_all(
            "SELECT room.id, room.owner_id, room.code, room.name, room.is_private, room.subject_tags, room.created_at "
            "FROM user_room JOIN room ON room.id = user_room.room_id "
            "WHERE user_room.user_id = %s ORDER BY user_room.created_at DESC LIMIT %s",
            (user_id, limit),
        )

    def get_owned_rooms_for_user(self, user_id, limit=8):
        return self.fetch_all(
            "SELECT id, owner_id, code, name, is_private, subject_tags, created_at "
            "FROM room WHERE owner_id = %s ORDER BY created_at DESC LIMIT %s",
            (user_id, limit),
        )

    def get_all_public_rooms(self):
        return self.fetch_all(
            "SELECT id, code, name, is_private, created_at FROM room WHERE is_private = 0 ORDER BY created_at DESC"
        )

    def get_all_rooms(self):
        return self.fetch_all(
            "SELECT r.id, r.owner_id, r.code, r.name, r.is_private, r.subject_tags, r.created_at, "
            "u.username AS owner_username "
            "FROM room r LEFT JOIN users u ON u.id = r.owner_id "
            "ORDER BY r.created_at DESC"
        )

    def update_room_name(self, room_id, new_name):
        return self.execute(
            "UPDATE room SET name = %s WHERE id = %s",
            (new_name, room_id),
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

    def log_room_action(self, username, room_code, room_name, action_type, duration_minutes=None, reason=None):
        ban_until = None
        if action_type == 'ban' and duration_minutes:
            ban_until = datetime.now() + timedelta(minutes=int(duration_minutes))
        return self.execute(
            "INSERT INTO room_actions (room_code, username, room_name, action_type, ban_until, reason) VALUES (%s, %s, %s, %s, %s, %s)",
            (room_code, username, room_name, action_type, ban_until, reason),
        )

    def log_moderation_action(self, room_id, room_code, actor_user_id, actor_username, target_username, action_type, duration_minutes=None, reason=None):
        self.create_moderation_log_table()
        return self.execute(
            "INSERT INTO room_moderation_log (room_id, room_code, actor_user_id, actor_username, target_username, action_type, duration_minutes, reason) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (room_id, room_code, actor_user_id, actor_username, target_username, action_type, duration_minutes, reason),
        )

    def get_moderation_log_for_room(self, room_code, limit=10):
        self.create_moderation_log_table()
        return self.fetch_all(
            "SELECT actor_username, target_username, action_type, duration_minutes, reason, created_at "
            "FROM room_moderation_log WHERE room_code = %s ORDER BY created_at DESC LIMIT %s",
            (room_code, limit),
        )

    def is_user_banned_from_room(self, username, room_code, room_name=None):
        query = (
            "SELECT * FROM room_actions WHERE username = %s AND action_type = 'ban' "
            "AND (ban_until IS NULL OR ban_until > NOW()) AND (room_code = %s OR room_name = %s) "
            "ORDER BY created_at DESC LIMIT 1"
        )
        row = self.fetch_one(query, (username, room_code, room_name or room_code))
        return row is not None


# module-level compatibility
_room_model = RoomModel()


def create_rooms_table():
    return _room_model.create_table()


def create_user_rooms_table():
    return _room_model.create_user_rooms_table()


def create_moderation_log_table():
    return _room_model.create_moderation_log_table()


def get_room_by_code(room_code):
    return _room_model.get_room_by_code(room_code)


def get_room_by_id(room_id):
    return _room_model.get_room_by_id(room_id)


def create_room(code, name, is_private, subject_tags, owner_id=None):
    return _room_model.create_room(code, name, is_private, subject_tags, owner_id)


def create_user_room(user_id, room_id, role='member'):
    return _room_model.create_user_room(user_id, room_id, role)


def is_user_in_room(user_id, room_id):
    return _room_model.is_user_in_room(user_id, room_id)


def set_user_room_role(user_id, room_id, role):
    return _room_model.set_user_room_role(user_id, room_id, role)


def get_user_room_role(user_id, room_id):
    return _room_model.get_user_room_role(user_id, room_id)


def get_room_members_with_roles(room_id):
    return _room_model.get_room_members_with_roles(room_id)


def get_joined_rooms_for_user(user_id, limit=8):
    return _room_model.get_joined_rooms_for_user(user_id, limit)


def get_owned_rooms_for_user(user_id, limit=8):
    return _room_model.get_owned_rooms_for_user(user_id, limit)


def get_all_public_rooms():
    return _room_model.get_all_public_rooms()


def get_all_rooms():
    return _room_model.get_all_rooms()


def update_room_name(room_id, new_name):
    return _room_model.update_room_name(room_id, new_name)


def delete_room_by_id(room_id):
    return _room_model.delete_room_by_id(room_id)


def delete_room_by_code(room_code):
    return _room_model.delete_room_by_code(room_code)


def log_room_action(username, room_code, room_name, action_type, duration_minutes=None, reason=None):
    return _room_model.log_room_action(username, room_code, room_name, action_type, duration_minutes, reason)


def log_moderation_action(room_id, room_code, actor_user_id, actor_username, target_username, action_type, duration_minutes=None, reason=None):
    return _room_model.log_moderation_action(room_id, room_code, actor_user_id, actor_username, target_username, action_type, duration_minutes, reason)


def get_moderation_log_for_room(room_code, limit=10):
    return _room_model.get_moderation_log_for_room(room_code, limit)


def is_user_banned_from_room(username, room_code, room_name=None):
    return _room_model.is_user_banned_from_room(username, room_code, room_name)
