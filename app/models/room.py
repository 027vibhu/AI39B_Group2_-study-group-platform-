from app.models.base_model import BaseModel
from app.models.database import ensure_database_exists, get_database_connection


class RoomModel(BaseModel):
    def __init__(self):
        super().__init__()

    @classmethod
    def create_rooms_table(cls):
        ensure_database_exists()

        connection = get_database_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "CREATE TABLE IF NOT EXISTS room ("
                    "id INT AUTO_INCREMENT PRIMARY KEY,"
                    "code VARCHAR(6) NOT NULL UNIQUE,"
                    "name VARCHAR(120) NOT NULL DEFAULT '',"
                    "subject_tag VARCHAR(80) NOT NULL DEFAULT '',"
                    "is_private TINYINT(1) NOT NULL DEFAULT 0,"
                    "created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"
                    ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
                )

                cursor.execute("SHOW COLUMNS FROM room LIKE 'subject_tag'")
                if not cursor.fetchone():
                    cursor.execute(
                        "ALTER TABLE room "
                        "ADD COLUMN subject_tag VARCHAR(80) NOT NULL DEFAULT ''"
                    )
        finally:
            connection.close()

    @classmethod
    def create_user_rooms_table(cls):
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

    @classmethod
    def get_room_by_code(cls, room_code):
        connection = get_database_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT id, code, name, subject_tag, is_private, created_at "
                    "FROM room WHERE code = %s LIMIT 1",
                    (room_code,),
                )
                return cursor.fetchone()
        finally:
            connection.close()

    @classmethod
    def get_room_by_id(cls, room_id):
        connection = get_database_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT id, code, name, subject_tag, is_private, created_at "
                    "FROM room WHERE id = %s LIMIT 1",
                    (room_id,),
                )
                return cursor.fetchone()
        finally:
            connection.close()

    @classmethod
    def create_room(cls, code, name, subject_tag, is_private):
        cls.create_rooms_table()

        connection = get_database_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO room (code, name, subject_tag, is_private) VALUES (%s, %s, %s, %s)",
                    (code, name, subject_tag, int(is_private)),
                )
                room_id = cursor.lastrowid
        finally:
            connection.close()

        return cls.get_room_by_id(room_id)

    @classmethod
    def create_user_room(cls, user_id, room_id):
        cls.create_user_rooms_table()

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

    @classmethod
    def get_joined_rooms_for_user(cls, user_id, limit=8):
        connection = get_database_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT room.id, room.code, room.name, room.subject_tag, room.is_private, room.created_at "
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

    @classmethod
    def delete_room_by_id(cls, room_id):
        connection = get_database_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM message WHERE room_id = %s", (room_id,))
                cursor.execute("DELETE FROM user_room WHERE room_id = %s", (room_id,))
                cursor.execute("DELETE FROM room WHERE id = %s", (room_id,))
                return cursor.rowcount
        finally:
            connection.close()

    @classmethod
    def delete_room_by_code(cls, room_code):
        room = cls.get_room_by_code(room_code)
        if not room:
            return 0
        return cls.delete_room_by_id(room['id'])


def create_rooms_table():
    return RoomModel.create_rooms_table()


def create_user_rooms_table():
    return RoomModel.create_user_rooms_table()


def get_room_by_code(room_code):
    return RoomModel.get_room_by_code(room_code)


def get_room_by_id(room_id):
    return RoomModel.get_room_by_id(room_id)


def create_room(code, name, subject_tag, is_private):
    return RoomModel.create_room(code, name, subject_tag, is_private)


def create_user_room(user_id, room_id):
    return RoomModel.create_user_room(user_id, room_id)


def get_joined_rooms_for_user(user_id, limit=8):
    return RoomModel.get_joined_rooms_for_user(user_id, limit)


def delete_room_by_id(room_id):
    return RoomModel.delete_room_by_id(room_id)


def delete_room_by_code(room_code):
    return RoomModel.delete_room_by_code(room_code)
