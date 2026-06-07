from app.models.base_model import BaseModel
from app.models.database import ensure_database_exists, get_database_connection


class RoomPresenceModel(BaseModel):
    """Model for tracking online/offline presence of members in a room."""

    def __init__(self):
        super().__init__()

    @classmethod
    def create_room_presence_table(cls):
        ensure_database_exists()

        connection = get_database_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "CREATE TABLE IF NOT EXISTS room_presence ("
                    "id INT AUTO_INCREMENT PRIMARY KEY,"
                    "room_id INT NOT NULL,"
                    "user_id INT NULL,"
                    "username VARCHAR(80) NOT NULL,"
                    "socket_id VARCHAR(128) NOT NULL UNIQUE,"
                    "is_online TINYINT(1) NOT NULL DEFAULT 1,"
                    "last_seen TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,"
                    "created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
                    "UNIQUE KEY uq_room_socket (room_id, socket_id),"
                    "INDEX idx_room_presence_room (room_id),"
                    "INDEX idx_room_presence_user (user_id),"
                    "FOREIGN KEY (room_id) REFERENCES room(id) ON DELETE CASCADE,"
                    "FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE"
                    ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
                )
        finally:
            connection.close()

    @classmethod
    def add_or_update_presence(cls, room_id, user_id, username, socket_id):
        cls.create_room_presence_table()

        connection = get_database_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO room_presence (room_id, user_id, username, socket_id, is_online, last_seen) "
                    "VALUES (%s, %s, %s, %s, 1, CURRENT_TIMESTAMP) "
                    "ON DUPLICATE KEY UPDATE user_id = VALUES(user_id), username = VALUES(username), "
                    "is_online = 1, last_seen = CURRENT_TIMESTAMP",
                    (room_id, user_id, username, socket_id),
                )
        finally:
            connection.close()

    @classmethod
    def set_offline_by_socket(cls, socket_id):
        connection = get_database_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE room_presence SET is_online = 0, last_seen = CURRENT_TIMESTAMP "
                    "WHERE socket_id = %s",
                    (socket_id,),
                )
        finally:
            connection.close()

    @classmethod
    def set_offline_for_user(cls, room_id, user_id):
        connection = get_database_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE room_presence SET is_online = 0, last_seen = CURRENT_TIMESTAMP "
                    "WHERE room_id = %s AND user_id = %s",
                    (room_id, user_id),
                )
        finally:
            connection.close()

    @classmethod
    def get_room_members(cls, room_id):
        connection = get_database_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT room_id, user_id, username, socket_id, is_online, last_seen "
                    "FROM room_presence WHERE room_id = %s "
                    "ORDER BY is_online DESC, username ASC",
                    (room_id,),
                )
                return cursor.fetchall()
        finally:
            connection.close()
