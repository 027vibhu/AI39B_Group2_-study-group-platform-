from app.models.base_model import BaseModel
from app.models.database import ensure_database_exists


class ChatAttachment(BaseModel):
    @property
    def table(self):
        return 'chat_attachment'

    @classmethod
    def ensure_table_exists(cls):
        ensure_database_exists()
        inst = cls()
        inst.execute(
            "CREATE TABLE IF NOT EXISTS chat_attachment ("
            "id INT AUTO_INCREMENT PRIMARY KEY,"
            "room_id INT NOT NULL,"
            "message_id INT NULL,"
            "username VARCHAR(50) NOT NULL,"
            "attachment_type ENUM('pdf','note') NOT NULL,"
            "original_filename VARCHAR(255) NULL,"
            "file_url TEXT NULL,"
            "note_content TEXT NULL,"
            "created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
            "INDEX idx_chat_attachment_room (room_id),"
            "INDEX idx_chat_attachment_message (message_id)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
        )

    def create_attachment(
        self,
        room_id,
        username,
        attachment_type,
        original_filename=None,
        file_url=None,
        note_content=None,
        message_id=None,
    ):
        self.ensure_table_exists()
        return self.execute(
            "INSERT INTO chat_attachment "
            "(room_id, message_id, username, attachment_type, original_filename, file_url, note_content) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (room_id, message_id, username, attachment_type, original_filename, file_url, note_content),
        )

    def get_attachments_for_room(self, room_id):
        return self.fetch_all(
            "SELECT id, room_id, message_id, username, attachment_type, original_filename, file_url, note_content, created_at "
            "FROM chat_attachment WHERE room_id = %s ORDER BY created_at ASC",
            (room_id,),
        )

    def get_attachments_for_message(self, message_id):
        return self.fetch_all(
            "SELECT id, room_id, message_id, username, attachment_type, original_filename, file_url, note_content, created_at "
            "FROM chat_attachment WHERE message_id = %s ORDER BY created_at ASC",
            (message_id,),
        )


_attachment_model = ChatAttachment()


def ensure_table_exists():
    return ChatAttachment.ensure_table_exists()


def create_attachment(
    room_id,
    username,
    attachment_type,
    original_filename=None,
    file_url=None,
    note_content=None,
    message_id=None,
):
    return _attachment_model.create_attachment(
        room_id,
        username,
        attachment_type,
        original_filename,
        file_url,
        note_content,
        message_id,
    )


def get_attachments_for_room(room_id):
    return _attachment_model.get_attachments_for_room(room_id)


def get_attachments_for_message(message_id):
    return _attachment_model.get_attachments_for_message(message_id)
