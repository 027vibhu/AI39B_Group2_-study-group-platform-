from app.controllers.base_controller import BaseController


class RoomController(BaseController):
    def __init__(self):
        super().__init__()
        try:
            import app.models.room as room_mod
        except Exception:
            room_mod = None

        self._room_mod = room_mod
        if room_mod and hasattr(room_mod, "RoomModel"):
            self.room_model = room_mod.RoomModel()
        else:
            self.room_model = None

    def browse_public_rooms(self):
        if self.room_model:
            self.room_model.create_table()
            return self.room_model.get_all_public_rooms()

        if self._room_mod:
            if hasattr(self._room_mod, "create_rooms_table"):
                self._room_mod.create_rooms_table()
            if hasattr(self._room_mod, "get_all_public_rooms"):
                return self._room_mod.get_all_public_rooms()

        return []