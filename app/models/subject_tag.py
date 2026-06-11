from app.models.base_model import BaseModel
from app.models.database import ensure_database_exists, get_database_connection


class SubjectTagModel(BaseModel):
    """Model for managing subject tags and their relationships with rooms."""

    def __init__(self):
        super().__init__()

    @classmethod
    def create_subject_tags_table(cls):
        """Create the subject_tags table to store all available subject tags."""
        ensure_database_exists()

        connection = get_database_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "CREATE TABLE IF NOT EXISTS subject_tags ("
                    "id INT AUTO_INCREMENT PRIMARY KEY,"
                    "tag_name VARCHAR(100) NOT NULL UNIQUE,"
                    "description VARCHAR(255) NOT NULL DEFAULT '',"
                    "created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"
                    ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
                )
        finally:
            connection.close()

    @classmethod
    def create_room_subject_tags_table(cls):
        """Create junction table to link rooms with multiple subject tags."""
        ensure_database_exists()

        connection = get_database_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "CREATE TABLE IF NOT EXISTS room_subject_tags ("
                    "id INT AUTO_INCREMENT PRIMARY KEY,"
                    "room_id INT NOT NULL,"
                    "tag_id INT NOT NULL,"
                    "created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
                    "UNIQUE KEY uq_room_tag (room_id, tag_id),"
                    "INDEX idx_room_tags_room (room_id),"
                    "INDEX idx_room_tags_tag (tag_id),"
                    "FOREIGN KEY (room_id) REFERENCES room(id) ON DELETE CASCADE,"
                    "FOREIGN KEY (tag_id) REFERENCES subject_tags(id) ON DELETE CASCADE"
                    ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
                )
        finally:
            connection.close()

    @classmethod
    def get_or_create_tag(cls, tag_name):
        """Get existing tag or create new one if it doesn't exist."""
        cls.create_subject_tags_table()

        connection = get_database_connection()
        try:
            with connection.cursor() as cursor:
                # Check if tag exists
                cursor.execute(
                    "SELECT id FROM subject_tags WHERE tag_name = %s LIMIT 1",
                    (tag_name,),
                )
                result = cursor.fetchone()
                
                if result:
                    return result['id']
                
                # Create new tag
                cursor.execute(
                    "INSERT INTO subject_tags (tag_name) VALUES (%s)",
                    (tag_name,),
                )
                return cursor.lastrowid
        finally:
            connection.close()

    @classmethod
    def get_all_tags(cls):
        """Retrieve all available subject tags."""
        cls.create_subject_tags_table()

        connection = get_database_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT id, tag_name, description FROM subject_tags "
                    "ORDER BY tag_name ASC"
                )
                return cursor.fetchall()
        finally:
            connection.close()

    @classmethod
    def get_room_tags(cls, room_id):
        """Get all subject tags for a specific room."""
        connection = get_database_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT st.id, st.tag_name, st.description "
                    "FROM subject_tags st "
                    "INNER JOIN room_subject_tags rst ON st.id = rst.tag_id "
                    "WHERE rst.room_id = %s "
                    "ORDER BY st.tag_name ASC",
                    (room_id,),
                )
                return cursor.fetchall()
        finally:
            connection.close()

    @classmethod
    def add_tag_to_room(cls, room_id, tag_name):
        """Add a subject tag to a room."""
        cls.create_room_subject_tags_table()

        tag_id = cls.get_or_create_tag(tag_name)

        connection = get_database_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT IGNORE INTO room_subject_tags (room_id, tag_id) VALUES (%s, %s)",
                    (room_id, tag_id),
                )
        finally:
            connection.close()

    @classmethod
    def remove_tag_from_room(cls, room_id, tag_id):
        """Remove a subject tag from a room."""
        connection = get_database_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM room_subject_tags WHERE room_id = %s AND tag_id = %s",
                    (room_id, tag_id),
                )
        finally:
            connection.close()