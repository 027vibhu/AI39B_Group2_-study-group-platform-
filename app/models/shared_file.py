from app.models.base_model import BaseModel
from app.models.database import ensure_database_exists


class SharedFileModel(BaseModel):
    @property
    def table(self):
        return 'shared_file'

    def create_table(self):
        ensure_database_exists()
        create_query = (
            "CREATE TABLE IF NOT EXISTS shared_file ("
            "id INT AUTO_INCREMENT PRIMARY KEY,"
            "room_id INT NOT NULL,"
            "uploader_username VARCHAR(50) NOT NULL,"
            "original_filename VARCHAR(255) NOT NULL,"
            "stored_filename VARCHAR(255) NOT NULL,"
            "mime_type VARCHAR(255) NOT NULL,"
            "file_size BIGINT NOT NULL DEFAULT 0,"
            "uploaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
            "INDEX idx_shared_file_room (room_id)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
        )
        return self.execute(create_query)

    def create_shared_file(self, room_id, uploader_username, original_filename, stored_filename, mime_type, file_size):
        self.create_table()
        return self.execute(
            "INSERT INTO shared_file (room_id, uploader_username, original_filename, stored_filename, mime_type, file_size) VALUES (%s, %s, %s, %s, %s, %s)",
            (room_id, uploader_username, original_filename, stored_filename, mime_type, file_size),
        )

    def get_shared_file_by_id(self, file_id):
        return self.fetch_one(
            "SELECT id, room_id, uploader_username, original_filename, stored_filename, mime_type, file_size, uploaded_at "
            "FROM shared_file WHERE id = %s LIMIT 1",
            (file_id,),
        )

    def get_shared_files_for_room(self, room_id):
        rows = self.fetch_all(
            "SELECT id, room_id, uploader_username, original_filename, stored_filename, mime_type, file_size, uploaded_at "
            "FROM shared_file WHERE room_id = %s ORDER BY uploaded_at DESC",
            (room_id,),
        )
        return rows


_shared_file_model = SharedFileModel()

# The following functions are simple wrappers around the SharedFileModel methods, and can be used directly in the application code.
def create_shared_files_table():
    return _shared_file_model.create_table()


def create_shared_file(room_id, uploader_username, original_filename, stored_filename, mime_type, file_size):
    return _shared_file_model.create_shared_file(room_id, uploader_username, original_filename, stored_filename, mime_type, file_size)


def get_shared_file_by_id(file_id):
    return _shared_file_model.get_shared_file_by_id(file_id)


def get_shared_files_for_room(room_id):
    return _shared_file_model.get_shared_files_for_room(room_id) 
# Note: The above functions are simple wrappers around the SharedFileModel methods, and can be used directly in the application code.