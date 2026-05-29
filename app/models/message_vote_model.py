from app.models.base_model import BaseModel


class MessageVoteModel(BaseModel):

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS message_votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            message_id INTEGER NOT NULL,
            vote_type TEXT NOT NULL CHECK(vote_type IN ('upvote', 'downvote')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            UNIQUE(user_id, message_id)
        );
        """

        self.execute_query(query)

    def add_vote(self, user_id, message_id, vote_type):
        query = """
        INSERT OR REPLACE INTO message_votes
        (user_id, message_id, vote_type)
        VALUES (?, ?, ?);
        """

        return self.execute_query(
            query,
            (user_id, message_id, vote_type)
        )

    def get_vote_count(self, message_id):
        query = """
        SELECT
            SUM(CASE WHEN vote_type = 'upvote' THEN 1 ELSE 0 END) as upvotes,
            SUM(CASE WHEN vote_type = 'downvote' THEN 1 ELSE 0 END) as downvotes
        FROM message_votes
        WHERE message_id = ?;
        """

        return self.fetch_one(query, (message_id,))