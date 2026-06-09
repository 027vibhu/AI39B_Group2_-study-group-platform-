from app.models.base_model import BaseModel
from app.models.database import ensure_database_exists


class ResourceVote(BaseModel):
    @property
    def table(self):
        return 'resource_vote'

    @classmethod
    def ensure_table_exists(cls):
        ensure_database_exists()
        inst = cls()
        inst.execute(
            "CREATE TABLE IF NOT EXISTS resource_vote ("
            "id INT AUTO_INCREMENT PRIMARY KEY,"
            "resource_id INT NOT NULL,"
            "user_id INT NOT NULL,"
            "vote_type ENUM('upvote','downvote') NOT NULL,"
            "created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
            "UNIQUE KEY ux_resource_user (resource_id, user_id),"
            "INDEX idx_resource_vote_resource (resource_id),"
            "INDEX idx_resource_vote_user (user_id)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
        )

    def create_or_update_vote(self, resource_id, user_id, vote_type):
        self.ensure_table_exists()
        return self.execute(
            "INSERT INTO resource_vote (resource_id, user_id, vote_type) VALUES (%s, %s, %s) "
            "ON DUPLICATE KEY UPDATE vote_type = VALUES(vote_type), created_at = CURRENT_TIMESTAMP",
            (resource_id, user_id, vote_type),
        )

    def remove_vote(self, resource_id, user_id):
        self.ensure_table_exists()
        return self.execute(
            "DELETE FROM resource_vote WHERE resource_id = %s AND user_id = %s",
            (resource_id, user_id),
        )

    def get_vote_count(self, resource_id):
        r = self.fetch_one(
            "SELECT "
            "COALESCE(CAST(SUM(vote_type = 'upvote') AS SIGNED), 0) AS upvotes, "
            "COALESCE(CAST(SUM(vote_type = 'downvote') AS SIGNED), 0) AS downvotes "
            "FROM resource_vote WHERE resource_id = %s",
            (resource_id,),
        )
        if not r:
            return {'upvotes': 0, 'downvotes': 0}

        return {
            'upvotes': int(r.get('upvotes') or 0),
            'downvotes': int(r.get('downvotes') or 0),
        }

    def get_user_vote(self, resource_id, user_id):
        row = self.fetch_one(
            "SELECT vote_type FROM resource_vote WHERE resource_id = %s AND user_id = %s LIMIT 1",
            (resource_id, user_id),
        )
        return row['vote_type'] if row else None


_rv = ResourceVote()


def ensure_table_exists():
    return ResourceVote.ensure_table_exists()


def create_or_update_vote(resource_id, user_id, vote_type):
    return _rv.create_or_update_vote(resource_id, user_id, vote_type)


def get_vote_count(resource_id):
    return _rv.get_vote_count(resource_id)


def get_user_vote(resource_id, user_id):
    return _rv.get_user_vote(resource_id, user_id)


def remove_vote(resource_id, user_id):
    return _rv.remove_vote(resource_id, user_id)
