from app.models.base_model import BaseModel


class RoomModel(BaseModel):
    """Model for room-related DB operations using raw SQL.

    Provides a method to fetch all public rooms (is_private = 0).
    """

    def get_all_public_rooms(self):
        query = (
            "SELECT id, code, name, is_private, created_at "
            "FROM room WHERE is_private = 0 "
            "ORDER BY created_at DESC"
        )
        return self.fetch_all(query)
