import json
from app.models.base_model import BaseModel
from app.models.database import ensure_database_exists


class WhiteboardModel(BaseModel):
    @property
    def table(self):
        return 'whiteboard'

    def create_table(self):
        ensure_database_exists()
        # Board objects (owner + shareable code).
        self.execute(
            "CREATE TABLE IF NOT EXISTS whiteboard ("
            "id INT AUTO_INCREMENT PRIMARY KEY,"
            "owner_id INT NULL,"
            "code VARCHAR(8) NOT NULL UNIQUE,"
            "title VARCHAR(120) NOT NULL DEFAULT '',"
            "created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
            "updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,"
            "INDEX idx_whiteboard_owner (owner_id)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
        )

        # Membership junction (mirrors user_room).
        self.execute(
            "CREATE TABLE IF NOT EXISTS whiteboard_member ("
            "id INT AUTO_INCREMENT PRIMARY KEY,"
            "whiteboard_id INT NOT NULL,"
            "user_id INT NOT NULL,"
            "created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
            "UNIQUE KEY uq_whiteboard_member (whiteboard_id, user_id),"
            "INDEX idx_whiteboard_member_board (whiteboard_id),"
            "INDEX idx_whiteboard_member_user (user_id)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
        )

        # Persisted canvas snapshot, one row per board.
        self.execute(
            "CREATE TABLE IF NOT EXISTS whiteboard_state ("
            "id INT AUTO_INCREMENT PRIMARY KEY,"
            "whiteboard_id INT NOT NULL,"
            "state LONGTEXT NOT NULL,"
            "updated_by_user_id INT NULL,"
            "updated_by_username VARCHAR(50) NULL,"
            "updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,"
            "UNIQUE KEY uq_whiteboard_state (whiteboard_id),"
            "INDEX idx_whiteboard_state_board (whiteboard_id)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
        )

        # Best-effort migration for installs that still have the old
        # room-keyed whiteboard_state table.
        try:
            self.execute("ALTER TABLE whiteboard_state ADD COLUMN whiteboard_id INT NOT NULL AFTER id")
        except Exception:
            pass
        try:
            self.execute("ALTER TABLE whiteboard_state ADD UNIQUE KEY uq_whiteboard_state (whiteboard_id)")
        except Exception:
            pass
        # Drop the legacy room-keyed unique key / index / column if they still exist.
        for stmt in (
            "ALTER TABLE whiteboard_state DROP INDEX uq_whiteboard_room",
            "ALTER TABLE whiteboard_state DROP INDEX idx_whiteboard_room",
            "ALTER TABLE whiteboard_state DROP COLUMN room_id",
        ):
            try:
                self.execute(stmt)
            except Exception:
                pass

    # --- Board CRUD -----------------------------------------------------
    def create_whiteboard(self, code, title, owner_id=None):
        self.create_table()
        wid = self.execute(
            "INSERT INTO whiteboard (code, title, owner_id) VALUES (%s, %s, %s)",
            (code, title, owner_id),
        )
        return self.get_whiteboard_by_id(wid)

    def get_whiteboard_by_code(self, code):
        return self.fetch_one(
            "SELECT id, owner_id, code, title, created_at, updated_at FROM whiteboard WHERE code = %s LIMIT 1",
            (code,),
        )

    def get_whiteboard_by_id(self, whiteboard_id):
        return self.fetch_one(
            "SELECT id, owner_id, code, title, created_at, updated_at FROM whiteboard WHERE id = %s LIMIT 1",
            (whiteboard_id,),
        )

    def touch(self, whiteboard_id):
        return self.execute(
            "UPDATE whiteboard SET updated_at = CURRENT_TIMESTAMP WHERE id = %s",
            (whiteboard_id,),
        )

    # --- Membership -----------------------------------------------------
    def add_member(self, user_id, whiteboard_id):
        self.create_table()
        return self.execute(
            "INSERT INTO whiteboard_member (whiteboard_id, user_id) VALUES (%s, %s) "
            "ON DUPLICATE KEY UPDATE id = id",
            (whiteboard_id, user_id),
        )

    def is_user_in_whiteboard(self, user_id, whiteboard_id):
        return bool(self.fetch_one(
            "SELECT 1 FROM whiteboard_member WHERE user_id = %s AND whiteboard_id = %s LIMIT 1",
            (user_id, whiteboard_id),
        ))

    def get_whiteboards_for_user(self, user_id, limit=50):
        return self.fetch_all(
            "SELECT w.id, w.owner_id, w.code, w.title, w.created_at, w.updated_at "
            "FROM whiteboard_member m JOIN whiteboard w ON w.id = m.whiteboard_id "
            "WHERE m.user_id = %s ORDER BY w.updated_at DESC LIMIT %s",
            (user_id, limit),
        )

    # --- Persisted state ------------------------------------------------
    def save_state(self, whiteboard_id, state_json, updated_by_user_id=None, updated_by_username=None):
        self.create_table()
        result = self.execute(
            "INSERT INTO whiteboard_state (whiteboard_id, state, updated_by_user_id, updated_by_username) "
            "VALUES (%s, %s, %s, %s) "
            "ON DUPLICATE KEY UPDATE state = %s, updated_by_user_id = %s, updated_by_username = %s, updated_at = CURRENT_TIMESTAMP",
            (whiteboard_id, state_json, updated_by_user_id, updated_by_username, state_json, updated_by_user_id, updated_by_username),
        )
        self.touch(whiteboard_id)
        return result

    def get_state(self, whiteboard_id):
        self.create_table()
        return self.fetch_one(
            "SELECT id, whiteboard_id, state, updated_by_user_id, updated_by_username, updated_at "
            "FROM whiteboard_state WHERE whiteboard_id = %s LIMIT 1",
            (whiteboard_id,),
        )

    def clear_state(self, whiteboard_id):
        self.create_table()
        return self.execute(
            "DELETE FROM whiteboard_state WHERE whiteboard_id = %s",
            (whiteboard_id,),
        )


_whiteboard_model = WhiteboardModel()


def create_whiteboard_table():
    return _whiteboard_model.create_table()


# Kept for backward compatibility with database.create_tables() registration.
def create_whiteboard_member_table():
    return _whiteboard_model.create_table()


def create_whiteboard(code, title, owner_id=None):
    return _whiteboard_model.create_whiteboard(code, title, owner_id)


def get_whiteboard_by_code(code):
    return _whiteboard_model.get_whiteboard_by_code(code)


def get_whiteboard_by_id(whiteboard_id):
    return _whiteboard_model.get_whiteboard_by_id(whiteboard_id)


def add_whiteboard_member(user_id, whiteboard_id):
    return _whiteboard_model.add_member(user_id, whiteboard_id)


def is_user_in_whiteboard(user_id, whiteboard_id):
    return _whiteboard_model.is_user_in_whiteboard(user_id, whiteboard_id)


def get_whiteboards_for_user(user_id, limit=50):
    return _whiteboard_model.get_whiteboards_for_user(user_id, limit)


def save_whiteboard_state(whiteboard_id, state_json, updated_by_user_id=None, updated_by_username=None):
    return _whiteboard_model.save_state(whiteboard_id, state_json, updated_by_user_id, updated_by_username)


def get_whiteboard_state(whiteboard_id):
    return _whiteboard_model.get_state(whiteboard_id)


def clear_whiteboard_state(whiteboard_id):
    return _whiteboard_model.clear_state(whiteboard_id)
