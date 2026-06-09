from app.models.base_model import BaseModel
from app.models.database import ensure_database_exists


class NotificationModel(BaseModel):
    @property
    def table(self):
        return 'room_notifications'

    def create_notifications_table(self):
        ensure_database_exists()
        return self.execute(
            "CREATE TABLE IF NOT EXISTS room_notifications ("
            "id INT AUTO_INCREMENT PRIMARY KEY,"
            "room_id INT NULL,"
            "room_code VARCHAR(6) NOT NULL," 
            "user_id INT NULL,"
            "username VARCHAR(50) NOT NULL," 
            "event_type ENUM('join', 'leave') NOT NULL," 
            "created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP," 
            "INDEX idx_room_notifications_room_code (room_code),"
            "INDEX idx_room_notifications_room_id (room_id),"
            "INDEX idx_room_notifications_user_id (user_id)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
        )

    def create_notification(self, room_id, room_code, username, event_type, user_id=None):
        self.create_notifications_table()
        return self.execute(
            "INSERT INTO room_notifications (room_id, room_code, user_id, username, event_type) "
            "VALUES (%s, %s, %s, %s, %s)",
            (room_id, room_code, user_id, username, event_type),
        )

    def get_notifications_for_room(self, room_code, limit=50):
        self.create_notifications_table()
        return self.fetch_all(
            "SELECT id, room_id, room_code, user_id, username, event_type, created_at "
            "FROM room_notifications WHERE room_code = %s "
            "ORDER BY created_at DESC LIMIT %s",
            (room_code, limit),
        )


notification_model = NotificationModel()


def create_notification(room_id, room_code, username, event_type, user_id=None):
    return notification_model.create_notification(room_id, room_code, username, event_type, user_id)


def get_notifications_for_room(room_code, limit=50):
    return notification_model.get_notifications_for_room(room_code, limit)
