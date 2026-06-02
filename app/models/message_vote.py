from app.models.base_model import BaseModel
from app.models.database import ensure_database_exists


class MessageVote(BaseModel):
    @property
    def table(self):
        return 'message_vote'

    @classmethod
    def ensure_table_exists(cls):
        ensure_database_exists()
        # create via an instance so BaseModel helpers are used
        inst = cls()
        inst.execute(
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

    def create_or_update_vote(self, message_id, user_id, vote_type):
        self.ensure_table_exists()
        return self.execute(
            "INSERT INTO message_vote (message_id, user_id, vote_type) VALUES (%s, %s, %s) "
            "ON DUPLICATE KEY UPDATE vote_type = VALUES(vote_type), created_at = CURRENT_TIMESTAMP",
            (message_id, user_id, vote_type),
        )

    def remove_vote(self, message_id, user_id):
        self.ensure_table_exists()
        return self.execute(
            "DELETE FROM message_vote WHERE message_id = %s AND user_id = %s",
            (message_id, user_id),
        )

    def get_vote_count(self, message_id):
        r = self.fetch_one(
            "SELECT "
            "COALESCE(CAST(SUM(vote_type = 'upvote') AS SIGNED), 0) AS upvotes, "
            "COALESCE(CAST(SUM(vote_type = 'downvote') AS SIGNED), 0) AS downvotes "
            "FROM message_vote WHERE message_id = %s",
            (message_id,),
        )
        if not r:
            return {'upvotes': 0, 'downvotes': 0}

        return {
            'upvotes': int(r.get('upvotes') or 0),
            'downvotes': int(r.get('downvotes') or 0),
        }

    def get_user_vote(self, message_id, user_id):
        row = self.fetch_one(
            "SELECT vote_type FROM message_vote WHERE message_id = %s AND user_id = %s LIMIT 1",
            (message_id, user_id),
        )
        return row['vote_type'] if row else None


# module-level compatibility helpers
_mv = MessageVote()


def ensure_table_exists():
    return MessageVote.ensure_table_exists()


def create_or_update_vote(message_id, user_id, vote_type):
    return _mv.create_or_update_vote(message_id, user_id, vote_type)


def get_vote_count(message_id):
    return _mv.get_vote_count(message_id)


def get_user_vote(message_id, user_id):
    return _mv.get_user_vote(message_id, user_id)


def remove_vote(message_id, user_id):
    return _mv.remove_vote(message_id, user_id)
