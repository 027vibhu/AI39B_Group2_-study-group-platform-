from app.models.database import ensure_database_exists
from app.models.base_model import BaseModel


class MessageModel(BaseModel):
    @property
    def table(self):
        return 'message'

    def create_table(self):
        ensure_database_exists()
        create_query = (
            "CREATE TABLE IF NOT EXISTS message ("
            "id INT AUTO_INCREMENT PRIMARY KEY,"
            "room_id INT NOT NULL,"
            "username VARCHAR(50) NOT NULL,"
            "content TEXT NOT NULL,"
            "timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
            "INDEX idx_message_room (room_id)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
        )
        return self.execute(create_query)

    def create_message(self, room_id, username, content):
        self.create_table()
        return self.execute(
            "INSERT INTO message (room_id, username, content) VALUES (%s, %s, %s)",
            (room_id, username, content),
        )

    def get_messages_for_room(self, room_id):
        rows = self.fetch_all(
            "SELECT id, room_id, username, content, timestamp "
            "FROM message WHERE room_id = %s ORDER BY timestamp ASC",
            (room_id,),
        )
        for row in rows:
            timestamp = row.get('timestamp')
            if timestamp and hasattr(timestamp, 'strftime'):
                row['time_label'] = timestamp.strftime('%I:%M %p')
            else:
                row['time_label'] = ''
        return rows


# module-level compatibility API
_message_model = MessageModel()


def create_messages_table():
    return _message_model.create_table()


def create_message(room_id, username, content):
    return _message_model.create_message(room_id, username, content)


def get_messages_for_room(room_id):
    return _message_model.get_messages_for_room(room_id)


def get_message_by_id(message_id):
    return _message_model.fetch_one(
        "SELECT id, room_id, username, content, timestamp FROM message WHERE id = %s LIMIT 1",
        (message_id,)
    )
