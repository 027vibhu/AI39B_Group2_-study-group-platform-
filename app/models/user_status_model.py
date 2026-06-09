from app.models.base_model import BaseModel

class UserStatusModel(BaseModel):
    def _init_(self):
        super()._init_()
        self.initialize_table()

    def initialize_table(self):
        query = """
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS is_online BOOLEAN DEFAULT FALSE,
        ADD COLUMN IF NOT EXISTS last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        """
        self.execute_query(query)

    def update_user_status(self, user_id, is_online):
        query = """
        UPDATE users 
        SET is_online = %s, last_seen = NOW() 
        WHERE id = %s;
        """
        self.execute_query(query, (is_online, user_id))

    def get_online_members(self):
        query = "SELECT id, username, is_online, last_seen FROM users WHERE is_online = TRUE;"
        return self.fetch_all(query)