from app.models.base_model import BaseModel
from app.models.database import ensure_database_exists


class PomodoroModel(BaseModel):
    @property
    def table(self):
        return 'pomodoro_session'

    def create_table(self):
        ensure_database_exists()
        create_query = (
            "CREATE TABLE IF NOT EXISTS pomodoro_session ("
            "id INT AUTO_INCREMENT PRIMARY KEY,"
            "user_id INT NOT NULL,"
            "room_id INT NULL,"
            "session_type ENUM('work','short_break','long_break') NOT NULL DEFAULT 'work',"
            "duration_seconds INT NOT NULL DEFAULT 1500,"  # 25 minutes default
            "status ENUM('scheduled','running','paused','completed','cancelled') NOT NULL DEFAULT 'scheduled',"
            "started_at DATETIME NULL,"
            "paused_at DATETIME NULL,"
            "ended_at DATETIME NULL,"
            "metadata JSON NULL,"
            "created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
            "updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,"
            "INDEX idx_pomodoro_user (user_id),"
            "INDEX idx_pomodoro_room (room_id)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
        )
        return self.execute(create_query)

    def create_session(self, user_id, duration_seconds=1500, session_type='work', room_id=None, metadata=None):
        self.create_table()
        return self.execute(
            "INSERT INTO pomodoro_session (user_id, room_id, duration_seconds, session_type, metadata) VALUES (%s, %s, %s, %s, %s)",
            (user_id, room_id, duration_seconds, session_type, metadata),
        )

    def get_session_by_id(self, session_id):
        return self.fetch_one(
            "SELECT id, user_id, room_id, session_type, duration_seconds, status, started_at, paused_at, ended_at, metadata, created_at, updated_at "
            "FROM pomodoro_session WHERE id = %s LIMIT 1",
            (session_id,),
        )

    def get_sessions_for_user(self, user_id, limit=50):
        return self.fetch_all(
            "SELECT id, user_id, room_id, session_type, duration_seconds, status, started_at, paused_at, ended_at, metadata, created_at, updated_at "
            "FROM pomodoro_session WHERE user_id = %s ORDER BY created_at DESC LIMIT %s",
            (user_id, limit),
        )

    def update_session(self, session_id, status=None, started_at=None, paused_at=None, ended_at=None, duration_seconds=None, metadata=None):
        updates = []
        params = []

        if status is not None:
            updates.append('status = %s')
            params.append(status)
        if started_at is not None:
            updates.append('started_at = %s')
            params.append(started_at)
        if paused_at is not None:
            updates.append('paused_at = %s')
            params.append(paused_at)
        if ended_at is not None:
            updates.append('ended_at = %s')
            params.append(ended_at)
        if duration_seconds is not None:
            updates.append('duration_seconds = %s')
            params.append(duration_seconds)
        if metadata is not None:
            updates.append('metadata = %s')
            params.append(metadata)

        if not updates:
            return 0

        params.append(session_id)
        query = f"UPDATE pomodoro_session SET {', '.join(updates)} WHERE id = %s"
        return self.execute(query, tuple(params))


_pomodoro_model = PomodoroModel()


def create_pomodoro_table():
    return _pomodoro_model.create_table()


def create_pomodoro_session(user_id, duration_seconds=1500, session_type='work', room_id=None, metadata=None):
    return _pomodoro_model.create_session(user_id, duration_seconds, session_type, room_id, metadata)


def get_pomodoro_session_by_id(session_id):
    return _pomodoro_model.get_session_by_id(session_id)


def get_pomodoro_sessions_for_user(user_id, limit=50):
    return _pomodoro_model.get_sessions_for_user(user_id, limit)


def update_pomodoro_session(session_id, status=None, started_at=None, paused_at=None, ended_at=None, duration_seconds=None, metadata=None):
    return _pomodoro_model.update_session(session_id, status, started_at, paused_at, ended_at, duration_seconds, metadata)
