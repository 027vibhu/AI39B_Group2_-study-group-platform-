from app.models.base_model import BaseModel
from app.models.database import ensure_database_exists


class FileStorage(BaseModel):
    @property
    def table(self):
        return 'file_storage'

    @classmethod
    def ensure_table_exists(cls):
        ensure_database_exists()
        inst = cls()
        inst.execute(
            "CREATE TABLE IF NOT EXISTS file_storage ("
            "id INT AUTO_INCREMENT PRIMARY KEY,"
            "filename VARCHAR(255) NOT NULL,"
            "original_filename VARCHAR(255) NOT NULL,"
            "folder_id INT NOT NULL,"
            "room_id INT NOT NULL,"
            "uploader_id INT NOT NULL,"
            "file_size INT NOT NULL,"
            "file_type VARCHAR(50),"
            "file_path VARCHAR(500) NOT NULL,"
            "description TEXT,"
            "created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
            "updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,"
            "INDEX idx_file_folder (folder_id),"
            "INDEX idx_file_room (room_id),"
            "INDEX idx_file_uploader (uploader_id),"
            "FOREIGN KEY (folder_id) REFERENCES folder(id) ON DELETE CASCADE,"
            "FOREIGN KEY (room_id) REFERENCES room(id) ON DELETE CASCADE"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
        )

    def upload_file(self, filename, original_filename, folder_id, room_id, uploader_id, 
                   file_size, file_type, file_path, description=None):
        self.ensure_table_exists()
        return self.execute(
            "INSERT INTO file_storage (filename, original_filename, folder_id, room_id, "
            "uploader_id, file_size, file_type, file_path, description) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (filename, original_filename, folder_id, room_id, uploader_id, 
             file_size, file_type, file_path, description),
        )

    def get_file_by_id(self, file_id):
        return self.fetch_one(
            "SELECT * FROM file_storage WHERE id = %s",
            (file_id,),
        )

    def get_files_in_folder(self, folder_id):
        return self.fetch_all(
            "SELECT * FROM file_storage WHERE folder_id = %s ORDER BY created_at DESC",
            (folder_id,),
        ) or []

    def get_files_in_room(self, room_id):
        return self.fetch_all(
            "SELECT * FROM file_storage WHERE room_id = %s ORDER BY created_at DESC",
            (room_id,),
        ) or []

    def get_files_by_uploader(self, uploader_id):
        return self.fetch_all(
            "SELECT * FROM file_storage WHERE uploader_id = %s ORDER BY created_at DESC",
            (uploader_id,),
        ) or []

    def update_file(self, file_id, description=None, original_filename=None):
        updates = []
        params = []
        
        if description is not None:
            updates.append("description = %s")
            params.append(description)
        if original_filename is not None:
            updates.append("original_filename = %s")
            params.append(original_filename)
        
        if not updates:
            return None
        
        params.append(file_id)
        query = f"UPDATE file_storage SET {', '.join(updates)} WHERE id = %s"
        return self.execute(query, tuple(params))

    def delete_file(self, file_id):
        return self.execute(
            "DELETE FROM file_storage WHERE id = %s",
            (file_id,),
        )

    def move_file_to_folder(self, file_id, new_folder_id):
        return self.execute(
            "UPDATE file_storage SET folder_id = %s WHERE id = %s",
            (new_folder_id, file_id),
        )

    def get_folder_file_count(self, folder_id):
        r = self.fetch_one(
            "SELECT COUNT(*) AS total FROM file_storage WHERE folder_id = %s",
            (folder_id,),
        )
        return r.get('total') if r else 0

    def get_total_folder_size(self, folder_id):
        r = self.fetch_one(
            "SELECT COALESCE(SUM(file_size), 0) AS total_size FROM file_storage WHERE folder_id = %s",
            (folder_id,),
        )
        return r.get('total_size') if r else 0


# module-level compatibility helpers
_file_storage = FileStorage()


def ensure_table_exists():
    return FileStorage.ensure_table_exists()


def upload_file(filename, original_filename, folder_id, room_id, uploader_id, 
               file_size, file_type, file_path, description=None):
    return _file_storage.upload_file(filename, original_filename, folder_id, room_id, 
                                     uploader_id, file_size, file_type, file_path, description)


def get_file_by_id(file_id):
    return _file_storage.get_file_by_id(file_id)


def get_files_in_folder(folder_id):
    return _file_storage.get_files_in_folder(folder_id)


def get_files_in_room(room_id):
    return _file_storage.get_files_in_room(room_id)


def get_files_by_uploader(uploader_id):
    return _file_storage.get_files_by_uploader(uploader_id)


def update_file(file_id, description=None, original_filename=None):
    return _file_storage.update_file(file_id, description, original_filename)


def delete_file(file_id):
    return _file_storage.delete_file(file_id)


def move_file_to_folder(file_id, new_folder_id):
    return _file_storage.move_file_to_folder(file_id, new_folder_id)


def get_folder_file_count(folder_id):
    return _file_storage.get_folder_file_count(folder_id)


def get_total_folder_size(folder_id):
    return _file_storage.get_total_folder_size(folder_id)
