import pymysql
from config import Config
from typing import Optional


def get_database_connection():
    return pymysql.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        port=Config.DB_PORT,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


def ensure_database_exists():
    connection = pymysql.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        port=Config.DB_PORT,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{Config.DB_NAME}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
    finally:
        connection.close()


def create_users_table():
    ensure_database_exists()

    connection = get_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS users ("
                "id INT AUTO_INCREMENT PRIMARY KEY,"
                "username VARCHAR(50) NOT NULL UNIQUE,"
                "email VARCHAR(255) NOT NULL UNIQUE,"
                "password_hash VARCHAR(255) NOT NULL,"
                "avatar_url VARCHAR(255) NOT NULL DEFAULT 'images/default_user_icon.jpg',"
                "first_name VARCHAR(80) NOT NULL DEFAULT '',"
                "last_name VARCHAR(80) NOT NULL DEFAULT '',"
                "school VARCHAR(160) NOT NULL DEFAULT '',"
                "address VARCHAR(255) NOT NULL DEFAULT '',"
                "bio TEXT,"
                "role VARCHAR(20) NOT NULL DEFAULT 'user',"
                "created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"
                ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
            )
            # Best-effort: add the role column on pre-existing tables.
            try:
                cursor.execute(
                    "ALTER TABLE users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'user' AFTER bio"
                )
            except Exception:
                pass
    finally:
        connection.close()


def get_user_by_identifier(identifier):
    connection = get_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, username, email, password_hash, avatar_url, "
                "first_name, last_name, school, address, bio, role, created_at "
                "FROM users WHERE username = %s OR email = %s LIMIT 1",
                (identifier, identifier),
            )
            return cursor.fetchone()
    finally:
        connection.close()


def get_user_by_email(email):
    connection = get_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, username, email, password_hash, avatar_url, "
                "first_name, last_name, school, address, bio, role, created_at "
                "FROM users WHERE email = %s LIMIT 1",
                (email,),
            )
            return cursor.fetchone()
    finally:
        connection.close()


def get_user_by_username(username):
    connection = get_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, username, email, password_hash, avatar_url, "
                "first_name, last_name, school, address, bio, role, created_at "
                "FROM users WHERE username = %s LIMIT 1",
                (username,),
            )
            return cursor.fetchone()
    finally:
        connection.close()


def get_user_by_id(user_id):
    connection = get_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, username, email, password_hash, avatar_url, "
                "first_name, last_name, school, address, bio, role, created_at "
                "FROM users WHERE id = %s LIMIT 1",
                (user_id,),
            )
            return cursor.fetchone()
    finally:
        connection.close()


def create_user(username, email, password_hash):
    create_users_table()

    connection = get_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                (username, email, password_hash),
            )
            return cursor.lastrowid
    finally:
        connection.close()


def ensure_admin_user():
    """Guarantee the single owner/admin account exists with the fixed credentials.

    Runs on startup. The account named Config.ADMIN_USERNAME is the only admin;
    every other user is forced back to the 'user' role so admin access can never
    be granted to anyone else.
    """
    from werkzeug.security import generate_password_hash

    create_users_table()

    username = Config.ADMIN_USERNAME
    email = Config.ADMIN_EMAIL
    password_hash = generate_password_hash(Config.ADMIN_PASSWORD)

    connection = get_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM users WHERE username = %s LIMIT 1", (username,)
            )
            row = cursor.fetchone()
            if row:
                # Keep the owner account in sync with the configured password/role.
                cursor.execute(
                    "UPDATE users SET email = %s, password_hash = %s, role = 'admin' WHERE id = %s",
                    (email, password_hash, row['id']),
                )
            else:
                cursor.execute(
                    "INSERT INTO users (username, email, password_hash, role) "
                    "VALUES (%s, %s, %s, 'admin')",
                    (username, email, password_hash),
                )

            # Enforce single-admin: nobody else may hold the admin role.
            cursor.execute(
                "UPDATE users SET role = 'user' WHERE username <> %s AND role = 'admin'",
                (username,),
            )
    finally:
        connection.close()


def update_user_avatar(user_id, avatar_url):
    connection = get_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET avatar_url = %s WHERE id = %s",
                (avatar_url, user_id),
            )
            return cursor.rowcount
    finally:
        connection.close()


def update_user_password(user_id, password_hash):
    connection = get_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET password_hash = %s WHERE id = %s",
                (password_hash, user_id),
            )
            return cursor.rowcount
    finally:
        connection.close()


def update_user_password_by_email(email, password_hash):
    connection = get_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET password_hash = %s WHERE email = %s",
                (password_hash, email),
            )
            return cursor.rowcount
    finally:
        connection.close()


def update_user_profile(user_id, first_name, last_name, school, address, bio):
    connection = get_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET first_name = %s, last_name = %s, school = %s, "
                "address = %s, bio = %s WHERE id = %s",
                (first_name, last_name, school, address, bio, user_id),
            )
            return cursor.rowcount
    finally:
        connection.close()


def get_all_users():
    connection = get_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, username, email, avatar_url, role, created_at "
                "FROM users ORDER BY created_at DESC"
            )
            return cursor.fetchall()
    finally:
        connection.close()


def set_user_role(user_id, role):
    connection = get_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET role = %s WHERE id = %s",
                (role, user_id),
            )
            return cursor.rowcount
    finally:
        connection.close()


def delete_user(user_id):
    """Delete a user and their owned content (rooms, notes, memberships)."""
    connection = get_database_connection()

    def _try(cursor, query, params):
        try:
            cursor.execute(query, params)
            return cursor.fetchall()
        except Exception:
            return []

    try:
        with connection.cursor() as cursor:
            # Rooms owned by the user, plus their messages and memberships.
            for room in _try(cursor, "SELECT id FROM room WHERE owner_id = %s", (user_id,)):
                room_id = room['id']
                _try(cursor, "DELETE FROM message WHERE room_id = %s", (room_id,))
                _try(cursor, "DELETE FROM user_room WHERE room_id = %s", (room_id,))
                _try(cursor, "DELETE FROM room WHERE id = %s", (room_id,))

            # Notes owned by the user, plus their shares.
            for note in _try(cursor, "SELECT id FROM notes WHERE user_id = %s", (user_id,)):
                _try(cursor, "DELETE FROM note_shares WHERE note_id = %s", (note['id'],))
            _try(
                cursor,
                "DELETE FROM note_shares WHERE shared_with_user_id = %s OR shared_by_user_id = %s",
                (user_id, user_id),
            )
            _try(cursor, "DELETE FROM notes WHERE user_id = %s", (user_id,))

            # The user's own room memberships, then the account.
            _try(cursor, "DELETE FROM user_room WHERE user_id = %s", (user_id,))
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            return cursor.rowcount
    finally:
        connection.close()


def create_room_actions_table():
    """
    Creates the table for tracking kicked or banned users.
    """
    ensure_database_exists()

    connection = get_database_connection()
    try:
        with connection.cursor() as cursor:
            # We keep both room_code and room_name for compatibility with older rows.
            sql = """
            CREATE TABLE IF NOT EXISTS room_actions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                room_code VARCHAR(6) NULL,
                username VARCHAR(50) NOT NULL,
                room_name VARCHAR(100) NOT NULL,
                action_type ENUM('kick', 'ban') NOT NULL,
                ban_until DATETIME NULL,
                reason TEXT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(sql)
            try:
                cursor.execute("ALTER TABLE room_actions ADD COLUMN room_code VARCHAR(6) NULL AFTER id")
            except Exception:
                pass
            try:
                cursor.execute("ALTER TABLE room_actions ADD INDEX idx_room_actions_room_code (room_code)")
            except Exception:
                pass

                try:
                    from app.models.exam_countdown import ensure_table_exists as _ensure_exam_table

                    _ensure_exam_table()
                except Exception:
                    pass
    finally:
        connection.close()


class Database:
    """Lightweight pymysql wrapper compatible with the README blueprint.

    Keeps the module-level helper functions for backward compatibility.
    """

    def __init__(self):
        self._conn = get_database_connection()

    def fetch_one(self, query: str, params: Optional[tuple] = None):
        with self._conn.cursor() as cur:
            cur.execute(query, params or ())
            return cur.fetchone()

    def fetch_all(self, query: str, params: Optional[tuple] = None):
        with self._conn.cursor() as cur:
            cur.execute(query, params or ())
            return cur.fetchall()

    def execute(self, query: str, params: Optional[tuple] = None):
        with self._conn.cursor() as cur:
            cur.execute(query, params or ())
            self._conn.commit()
            try:
                return cur.lastrowid
            except Exception:
                return cur.rowcount

    def close(self):
        try:
            self._conn.close()
        except Exception:
            pass

    @staticmethod
    def create_tables():
        """Attempt to create core tables by delegating to available modules.

        This keeps behavior consistent with the existing project (which
        creates several tables at startup).
        """
        # Ensure database exists and create core users table
        ensure_database_exists()
        create_users_table()

        # Bootstrap the single owner/admin account.
        try:
            ensure_admin_user()
        except Exception:
            pass

        # Try to create other tables if their modules are available
        try:
            # room tables
            from app.models.room import create_rooms_table, create_user_rooms_table

            create_rooms_table()
            create_user_rooms_table()
        except Exception:
            pass

        try:
            from app.models.message import create_messages_table

            create_messages_table()
        except Exception:
            pass

        try:
            from app.models.message_vote import MessageVote

            MessageVote.ensure_table_exists()
        except Exception:
            pass

        try:
            from app.models.exam_countdown import create_exam_countdown_table

            create_exam_countdown_table()
        except Exception:
            pass

        try:
            from app.models.chat_attachment import create_attachment, ensure_table_exists

            ensure_table_exists()
        except Exception:
            pass

        try:
            from app.models.database import create_room_actions_table

            create_room_actions_table()
        except Exception:
            pass

        try:
            from app.models.room import create_moderation_log_table

            create_moderation_log_table()
        except Exception:
            pass

        try:
            from app.models.join_leave_notification import create_join_leave_notifications_table

            create_join_leave_notifications_table()
        except Exception:
            pass

        try:
            from app.models.shared_file import create_shared_files_table

            create_shared_files_table()
        except Exception:
            pass

        try:
            from app.models.whiteboard import create_whiteboard_table, create_whiteboard_member_table

            create_whiteboard_table()
            create_whiteboard_member_table()
        except Exception:
            pass

        try:
            from app.models.pomodoro import create_pomodoro_table

            create_pomodoro_table()
        except Exception:
            pass

        try:
            from app.models.presence_model import room_presence_model

            room_presence_model.create_room_presence_table()
        except Exception:
            pass

        try:
            from app.models.study_streak import create_study_streaks_table

            create_study_streaks_table()
        except Exception:
            pass

        try:
            from app.models.deactivated_account import ensure_table_exists as _ensure_deactivated_table

            _ensure_deactivated_table()
        except Exception:
            pass
