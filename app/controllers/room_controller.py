from app.models.room_model import RoomModel


class RoomController:
    def __init__(self):
        self.room_model = RoomModel()

    def browse_public_rooms(self):
        self.room_model.create_table()
        return self.room_model.get_all_public_rooms()