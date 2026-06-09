from app.models.base_model import BaseModel
from app.models.database import ensure_database_exists


class Folder(BaseModel):
    @property
    def table(self):
        return 'folder'

    @classmethod
    def ensure_table_exists(cls):
        ensure_database_exists()
        inst = cls()
        inst.execute(
            "CREATE TABLE IF NOT EXISTS folder ("
            "id INT AUTO_INCREMENT PRIMARY KEY,"
            "name VARCHAR(255) NOT NULL,"
            "parent_folder_id INT,"
            "room_id INT NOT NULL,"
            "owner_id INT NOT NULL,"
            "description TEXT,"
            "created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
            "updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,"
            "INDEX idx_folder_parent (parent_folder_id),"
            "INDEX idx_folder_room (room_id),"
            "INDEX idx_folder_owner (owner_id),"
            "FOREIGN KEY (parent_folder_id) REFERENCES folder(id) ON DELETE CASCADE"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
        )

    def create_folder(self, name, room_id, owner_id, parent_folder_id=None, description=None):
        self.ensure_table_exists()
        return self.execute(
            "INSERT INTO folder (name, room_id, owner_id, parent_folder_id, description) "
            "VALUES (%s, %s, %s, %s, %s)",
            (name, room_id, owner_id, parent_folder_id, description),
        )

    def get_folder_by_id(self, folder_id):
        return self.fetch_one(
            "SELECT * FROM folder WHERE id = %s",
            (folder_id,),
        )

    def get_folders_in_room(self, room_id, parent_folder_id=None):
        if parent_folder_id is None:
            rows = self.fetch_all(
                "SELECT * FROM folder WHERE room_id = %s AND parent_folder_id IS NULL "
                "ORDER BY created_at DESC",
                (room_id,),
            )
        else:
            rows = self.fetch_all(
                "SELECT * FROM folder WHERE room_id = %s AND parent_folder_id = %s "
                "ORDER BY created_at DESC",
                (room_id, parent_folder_id),
            )
        return rows or []

    def get_folder_contents(self, folder_id):
        """Get all folders inside a specific folder"""
        return self.fetch_all(
            "SELECT * FROM folder WHERE parent_folder_id = %s ORDER BY created_at DESC",
            (folder_id,),
        )

    def update_folder(self, folder_id, name=None, description=None):
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = %s")
            params.append(name)
        if description is not None:
            updates.append("description = %s")
            params.append(description)
        
        if not updates:
            return None
        
        params.append(folder_id)
        query = f"UPDATE folder SET {', '.join(updates)} WHERE id = %s"
        return self.execute(query, tuple(params))

    def delete_folder(self, folder_id):
        return self.execute(
            "DELETE FROM folder WHERE id = %s",
            (folder_id,),
        )

    def get_folder_path(self, folder_id):
        """Get the full path of a folder from root to current"""
        folder = self.get_folder_by_id(folder_id)
        if not folder:
            return []
        
        path = [folder]
        while folder.get('parent_folder_id'):
            folder = self.get_folder_by_id(folder.get('parent_folder_id'))
            if folder:
                path.insert(0, folder)
            else:
                break
        return path


# module-level compatibility helpers
_folder = Folder()


def ensure_table_exists():
    return Folder.ensure_table_exists()


def create_folder(name, room_id, owner_id, parent_folder_id=None, description=None):
    return _folder.create_folder(name, room_id, owner_id, parent_folder_id, description)


def get_folder_by_id(folder_id):
    return _folder.get_folder_by_id(folder_id)


def get_folders_in_room(room_id, parent_folder_id=None):
    return _folder.get_folders_in_room(room_id, parent_folder_id)


def get_folder_contents(folder_id):
    return _folder.get_folder_contents(folder_id)


def update_folder(folder_id, name=None, description=None):
    return _folder.update_folder(folder_id, name, description)


def delete_folder(folder_id):
    return _folder.delete_folder(folder_id)


def get_folder_path(folder_id):
    return _folder.get_folder_path(folder_id)
