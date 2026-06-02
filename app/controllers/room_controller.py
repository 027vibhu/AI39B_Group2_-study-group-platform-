<<<<<<< HEAD
import random

from app.controllers.base_controller import BaseController
from app.models.room import RoomModel
=======
from app.controllers.base_controller import BaseController
>>>>>>> 60ab2a74498b01c2f9451141b9df7fa3c555ab46


class RoomController(BaseController):
    def __init__(self):
        super().__init__()
<<<<<<< HEAD

    def create_room(self, room_name: str, subject_tag: str, submitted_code: str, is_private: bool):
        submitted_code = (submitted_code or '').strip().upper()
        if len(submitted_code) == 6 and submitted_code.isalnum() and not RoomModel.get_room_by_code(submitted_code):
            code = submitted_code
        else:
            code = self.generate_unique_room_code()

        return RoomModel.create_room(
            code,
            room_name or f'Room {code}',
            subject_tag,
            is_private,
        )

    def generate_unique_room_code(self) -> str:
        while True:
            code = str(random.randint(100000, 999999))
            if not RoomModel.get_room_by_code(code):
                return code
=======
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
>>>>>>> 60ab2a74498b01c2f9451141b9df7fa3c555ab46
