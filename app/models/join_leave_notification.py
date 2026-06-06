from app.models.base_model import BaseModel
from app.models.database import ensure_database_exists


class JoinLeaveNotificationModel(BaseModel):
    @property
    def table(self):
        return 'join_leave_notifications'

    def create_table(self):
        ensure_database_exists()
        return self.execute(
            "CREATE TABLE IF NOT EXISTS join_leave_notifications ("
            "id INT AUTO_INCREMENT PRIMARY KEY,"
            "room_id INT NOT NULL,"
            "user_id INT NULL,"
            "username VARCHAR(50) NOT NULL,"
            "action_type ENUM('join','leave') NOT NULL,"
            "message TEXT NULL,"
            "created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP," 
            "INDEX idx_join_leave_notifications_room (room_id),"
            "INDEX idx_join_leave_notifications_action (action_type)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
        )

    def add_notification(self, room_id, user_id, username, action_type, message=None):
        self.create_table()
        return self.execute(
            "INSERT INTO join_leave_notifications (room_id, user_id, username, action_type, message) "
            "VALUES (%s, %s, %s, %s, %s)",
            (room_id, user_id, username, action_type, message),
        )

    def get_room_notifications(self, room_id, limit=50):
        self.create_table()
        return self.fetch_all(
            "SELECT id, room_id, user_id, username, action_type, message, created_at "
            "FROM join_leave_notifications WHERE room_id = %s "
            "ORDER BY created_at DESC LIMIT %s",
            (room_id, limit),
        )


join_leave_notification_model = JoinLeaveNotificationModel()


def create_join_leave_notifications_table():
    return join_leave_notification_model.create_table()


def add_join_leave_notification(room_id, user_id, username, action_type, message=None):
    return join_leave_notification_model.add_notification(
        room_id, user_id, username, action_type, message
    )


def get_join_leave_notifications(room_id, limit=50):
    return join_leave_notification_model.get_room_notifications(room_id, limit)
