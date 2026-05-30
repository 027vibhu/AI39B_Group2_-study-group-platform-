from app.models.database import ensure_database_exists, get_database_connection

from datetime import datetime, timedelta

def create_rooms_table():
    ensure_database_exists()

    connection = get_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS room ("
                "id INT AUTO_INCREMENT PRIMARY KEY,"
                "code VARCHAR(6) NOT NULL UNIQUE,"
                "name VARCHAR(120) NOT NULL DEFAULT '',"
                "is_private TINYINT(1) NOT NULL DEFAULT 0,"
                "subject_tags VARCHAR(255) DEFAULT '',"
                "created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"
                ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
            )
            cursor.execute("SHOW COLUMNS FROM room LIKE %s", ("subject_tags",))
            if not cursor.fetchone():
                cursor.execute(
                    "ALTER TABLE room "
                    "ADD COLUMN subject_tags VARCHAR(255) DEFAULT ''"
                )
    finally:
        connection.close()


def create_user_rooms_table():
    ensure_database_exists()

    connection = get_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
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
    finally:
        connection.close()


def get_room_by_code(room_code):
    connection = get_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, code, name, is_private, subject_tags, created_at "
                "FROM room WHERE code = %s LIMIT 1",
                (room_code,),
            )
            return cursor.fetchone()
    finally:
        connection.close()


def get_room_by_id(room_id):
    connection = get_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, code, name, is_private, subject_tags, created_at "
                "FROM room WHERE id = %s LIMIT 1",
                (room_id,),
            )
            return cursor.fetchone()
    finally:
        connection.close()


def create_room(code, name, is_private, subject_tags):
    create_rooms_table()

    connection = get_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO room (code, name, is_private, subject_tags) "
                "VALUES (%s, %s, %s, %s)",
                (code, name, int(is_private), subject_tags),
            )
            room_id = cursor.lastrowid
    finally:
        connection.close()

    return get_room_by_id(room_id)


def create_user_room(user_id, room_id):
    create_user_rooms_table()

    connection = get_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO user_room (user_id, room_id) VALUES (%s, %s) "
                "ON DUPLICATE KEY UPDATE id = id",
                (user_id, room_id),
            )
            return cursor.rowcount
    finally:
        connection.close()


def is_user_in_room(user_id, room_id):
    connection = get_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM user_room WHERE user_id = %s AND room_id = %s LIMIT 1",
                (user_id, room_id),
            )
            return cursor.fetchone() is not None
    finally:
        connection.close()


def get_joined_rooms_for_user(user_id, limit=8):
    connection = get_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT room.id, room.code, room.name, room.is_private, room.subject_tags, room.created_at "
                "FROM user_room "
                "JOIN room ON room.id = user_room.room_id "
                "WHERE user_room.user_id = %s "
                "ORDER BY user_room.created_at DESC "
                "LIMIT %s",
                (user_id, limit),
            )
            return cursor.fetchall()
    finally:
        connection.close()


def get_all_public_rooms():
    """Return all public rooms (is_private = 0), newest first."""
    connection = get_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, code, name, is_private, created_at "
                "FROM room WHERE is_private = 0 "
                "ORDER BY created_at DESC",
            )
            return cursor.fetchall()
    finally:
        connection.close()


def delete_room_by_id(room_id):
    connection = get_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM message WHERE room_id = %s", (room_id,))
            cursor.execute("DELETE FROM user_room WHERE room_id = %s", (room_id,))
            cursor.execute("DELETE FROM room WHERE id = %s", (room_id,))
            return cursor.rowcount
    finally:
        connection.close()


def delete_room_by_code(room_code):
    room = get_room_by_code(room_code)
    if not room:
        return 0
    return delete_room_by_id(room['id'])


def log_room_action(username, room_name, action_type, duration_minutes=None, reason=None):
    """
    Logs a kick or ban action into the database.
    If it's a ban, it calculates the 'ban_until' time using duration_minutes.
    """
    connection = get_database_connection()
    try:
        with connection.cursor() as cursor:
            ban_until = None
            
            # Calculate the expiration time only if it's a ban with a duration
            if action_type == 'ban' and duration_minutes:
                ban_until = datetime.now() + timedelta(minutes=int(duration_minutes))

            sql = """
                INSERT INTO room_actions (username, room_name, action_type, ban_until, reason)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (username, room_name, action_type, ban_until, reason))
    finally:
        connection.close()


def is_user_banned_from_room(username, room_name):
    """
    Checks if a user is currently banned from a specific room.
    Returns True if banned, False otherwise.
    """
    connection = get_database_connection()
    try:
        with connection.cursor() as cursor:
            # Look for an active ban where the expiration time is still in the future
            sql = """
                SELECT * FROM room_actions 
                WHERE username = %s 
                  AND room_name = %s 
                  AND action_type = 'ban'
                  AND (ban_until IS NULL OR ban_until > NOW())
                ORDER BY created_at DESC LIMIT 1
            """
            cursor.execute(sql, (username, room_name))
            result = cursor.fetchone()
            
            # If a record is found, they are banned
            return result is not None
    finally:
        connection.close()
        
# ... Keep ALL of your existing code exactly as it is ...

# 1. ADD THIS NEW DATABASE HELPER FUNCTION AT THE BOTTOM
def get_all_public_rooms():
    """Queries the database for all public rooms."""
    connection = get_database_connection()
    try:
        with connection.cursor() as cursor:
            # is_private = 0 means the room is public
            cursor.execute(
                "SELECT id, code, name, is_private, created_at "
                "FROM room WHERE is_private = 0 ORDER BY created_at DESC"
            )
            return cursor.fetchall()
    finally:
        connection.close()


# 2. ADD THIS DOMAIN CLASS AT THE VERY BOTTOM FOR OOP ENCAPSULATION
class Room:
    def __init__(self, room_id, code, name, is_private, created_at=None):
        self.room_id = room_id
        self.code = code
        self.name = name
        self.is_private = bool(is_private)
        self.created_at = created_at

    def to_dict(self):
        """Converts the object properties into a clean dictionary payload for the frontend."""
        return {
            "id": self.room_id,
            "code": self.code,
            "name": self.name,
            "is_public": not self.is_private,  # Flips it to make it intuitive for front-end consumption
            "created_at": str(self.created_at) if self.created_at else None
        }
