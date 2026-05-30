from app.models.base_model import BaseModel
from app.models.database import ensure_database_exists, get_database_connection


class MessageVote(BaseModel):
    @classmethod
    def get_database_connection(cls):
        return get_database_connection()

    @classmethod
    def ensure_table_exists(cls):
        ensure_database_exists()

        connection = cls.get_database_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "CREATE TABLE IF NOT EXISTS message_vote ("
                    "id INT AUTO_INCREMENT PRIMARY KEY,"
                    "message_id INT NOT NULL,"
                    "user_id INT NOT NULL,"
                    "vote_type ENUM('upvote','downvote') NOT NULL,"
                    "created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
                    "UNIQUE KEY ux_message_user (message_id, user_id),"
                    "INDEX idx_message_vote_message (message_id),"
                    "INDEX idx_message_vote_user (user_id)"
                    ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
                )
        finally:
            connection.close()

    @classmethod
    def create_or_update_vote(cls, message_id, user_id, vote_type):
        cls.ensure_table_exists()

        connection = cls.get_database_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO message_vote (message_id, user_id, vote_type) VALUES (%s, %s, %s) "
                    "ON DUPLICATE KEY UPDATE vote_type = VALUES(vote_type), created_at = CURRENT_TIMESTAMP",
                    (message_id, user_id, vote_type),
                )
                return cursor.lastrowid
        finally:
            connection.close()

    @classmethod
    def get_vote_count(cls, message_id):
        connection = cls.get_database_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT "
                    "SUM(vote_type = 'upvote') AS upvotes, "
                    "SUM(vote_type = 'downvote') AS downvotes "
                    "FROM message_vote WHERE message_id = %s",
                    (message_id,),
                )
                return cursor.fetchone() or {'upvotes': 0, 'downvotes': 0}
        finally:
            connection.close()

    @classmethod
    def get_user_vote(cls, message_id, user_id):
        connection = cls.get_database_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT vote_type FROM message_vote WHERE message_id = %s AND user_id = %s LIMIT 1",
                    (message_id, user_id),
                )
                row = cursor.fetchone()
                return row['vote_type'] if row else None
        finally:
            connection.close()
