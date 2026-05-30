from app.models.base_model import BaseModel
from app.models.database import ensure_database_exists, get_database_connection


class RoomPresenceModel(BaseModel):
    def create_room_presence_table(self):
        ensure_database_exists()
        connection = get_database_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "CREATE TABLE IF NOT EXISTS room_presence ("
                    "id INT AUTO_INCREMENT PRIMARY KEY,"
                    "user_id INT NOT NULL,"
                    "room_id INT NOT NULL,"
                    "username VARCHAR(50) NOT NULL,"
                    "status VARCHAR(10) NOT NULL DEFAULT 'offline',"
                    "last_seen TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,"
                    "created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
                    "UNIQUE KEY uq_room_user (user_id, room_id),"
                    "INDEX idx_room_presence_room (room_id),"
                    "INDEX idx_room_presence_user (user_id)"
                    ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
                )
        finally:
            connection.close()

    def set_presence(self, user_id, room_id, username, status):
        self.create_room_presence_table()
        return self.execute(
            "INSERT INTO room_presence (user_id, room_id, username, status) "
            "VALUES (%s, %s, %s, %s) "
            "ON DUPLICATE KEY UPDATE username = %s, status = %s, last_seen = CURRENT_TIMESTAMP",
            (user_id, room_id, username, status, username, status),
        )

    def set_user_online(self, user_id, room_id, username):
        return self.set_presence(user_id, room_id, username, 'online')

    def set_user_offline(self, user_id, room_id, username):
        return self.set_presence(user_id, room_id, username, 'offline')

    def get_room_presence(self, room_id):
        self.create_room_presence_table()
        return self.fetch_all(
            "SELECT user_id, username, status, last_seen, created_at "
            "FROM room_presence WHERE room_id = %s "
            "ORDER BY status DESC, username ASC",
            (room_id,),
        )

    def get_online_users(self, room_id):
        return self.fetch_all(
            "SELECT user_id, username, status "
            "FROM room_presence WHERE room_id = %s AND status = 'online' "
            "ORDER BY username ASC",
            (room_id,),
        )

    def get_offline_users(self, room_id):
        return self.fetch_all(
            "SELECT user_id, username, status "
            "FROM room_presence WHERE room_id = %s AND status = 'offline' "
            "ORDER BY username ASC",
            (room_id,),
        )


room_presence_model = RoomPresenceModel()


def set_user_online(user_id, room_id, username):
    return room_presence_model.set_user_online(user_id, room_id, username)


def set_user_offline(user_id, room_id, username):
    return room_presence_model.set_user_offline(user_id, room_id, username)


def get_room_presence(room_id):
    return room_presence_model.get_room_presence(room_id)


def get_online_users(room_id):
    return room_presence_model.get_online_users(room_id)


def get_offline_users(room_id):
    return room_presence_model.get_offline_users(room_id)
