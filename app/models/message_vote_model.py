from app.models.database import get_database_connection


class MessageVoteModel:
    def create_table(self):
        connection = get_database_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "CREATE TABLE IF NOT EXISTS message_votes ("
                    "id INT AUTO_INCREMENT PRIMARY KEY,"
                    "user_id INT NOT NULL,"
                    "message_id INT NOT NULL,"
                    "vote_type VARCHAR(16) NOT NULL,"
                    "created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
                    "UNIQUE KEY uq_user_message (user_id, message_id)"
                    ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
                )
        finally:
            connection.close()

    def add_vote(self, user_id, message_id, vote_type):
        connection = get_database_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO message_votes (user_id, message_id, vote_type) "
                    "VALUES (%s, %s, %s) "
                    "ON DUPLICATE KEY UPDATE vote_type = VALUES(vote_type)",
                    (user_id, message_id, vote_type),
                )
                return cursor.rowcount
        finally:
            connection.close()

    def get_vote_count(self, message_id):
        connection = get_database_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT "
                    "SUM(CASE WHEN vote_type = 'upvote' THEN 1 ELSE 0 END) as upvotes, "
                    "SUM(CASE WHEN vote_type = 'downvote' THEN 1 ELSE 0 END) as downvotes "
                    "FROM message_votes WHERE message_id = %s",
                    (message_id,),
                )
                return cursor.fetchone()
        finally:
            connection.close()