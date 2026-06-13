from app.models.base_model import BaseModel
from app.models.database import ensure_database_exists


class Whiteboard(BaseModel):
    @property
    def table(self):
        return 'whiteboard_drawings'

    @classmethod
    def ensure_table_exists(cls):
        ensure_database_exists()
        inst = cls()
        inst.execute(
            "CREATE TABLE IF NOT EXISTS whiteboard_drawings ("
            "id INT AUTO_INCREMENT PRIMARY KEY,"
            "room_id INT NOT NULL,"
            "creator_user_id INT NOT NULL,"
            "title VARCHAR(255) NOT NULL DEFAULT '',"
            "drawing_data LONGTEXT NOT NULL,"
            "created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
            "updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,"
            "INDEX idx_whiteboard_room (room_id),"
            "INDEX idx_whiteboard_creator (creator_user_id)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
        )

    def save_drawing(self, room_id, creator_user_id, drawing_data, title=''):
        self.ensure_table_exists()
        return self.execute(
            "INSERT INTO whiteboard_drawings (room_id, creator_user_id, drawing_data, title) "
            "VALUES (%s, %s, %s, %s)",
            (room_id, creator_user_id, drawing_data, title),
        )

    def update_drawing(self, drawing_id, drawing_data, title=None):
        self.ensure_table_exists()
        if title is None:
            return self.execute(
                "UPDATE whiteboard_drawings SET drawing_data = %s WHERE id = %s",
                (drawing_data, drawing_id),
            )

        return self.execute(
            "UPDATE whiteboard_drawings SET drawing_data = %s, title = %s WHERE id = %s",
            (drawing_data, title, drawing_id),
        )

    def get_drawing_by_id(self, drawing_id):
        self.ensure_table_exists()
        return self.fetch_one(
            "SELECT id, room_id, creator_user_id, title, drawing_data, created_at, updated_at "
            "FROM whiteboard_drawings WHERE id = %s LIMIT 1",
            (drawing_id,),
        )

    def get_drawings_for_room(self, room_id):
        self.ensure_table_exists()
        return self.fetch_all(
            "SELECT id, room_id, creator_user_id, title, drawing_data, created_at, updated_at "
            "FROM whiteboard_drawings WHERE room_id = %s ORDER BY updated_at DESC",
            (room_id,),
        )


_whiteboard = Whiteboard()


def ensure_table_exists():
    return Whiteboard.ensure_table_exists()


def save_whiteboard_drawing(room_id, creator_user_id, drawing_data, title=''):
    return _whiteboard.save_drawing(room_id, creator_user_id, drawing_data, title)


def update_whiteboard_drawing(drawing_id, drawing_data, title=None):
    return _whiteboard.update_drawing(drawing_id, drawing_data, title)


def get_whiteboard_drawing(drawing_id):
    return _whiteboard.get_drawing_by_id(drawing_id)


def get_whiteboard_drawings_for_room(room_id):
    return _whiteboard.get_drawings_for_room(room_id)
