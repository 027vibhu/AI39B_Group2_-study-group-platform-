import random

from app.controllers.base_controller import BaseController
from app.models.room import RoomModel


class RoomController(BaseController):
    def __init__(self):
        super().__init__()
        self._room_model = RoomModel()

    def browse_public_rooms(self):
        """Return all public rooms from the database."""
        self._room_model.create_table()
        return self._room_model.get_all_public_rooms()

    def create_room(self, room_name: str, subject_tag: str, submitted_code: str, is_private: bool, owner_id=None):
        submitted_code = (submitted_code or '').strip().upper()
        if len(submitted_code) == 6 and submitted_code.isalnum() and not self._room_model.get_room_by_code(submitted_code):
            code = submitted_code
        else:
            code = self.generate_unique_room_code()

        return self._room_model.create_room(
            code,
            room_name or f'Room {code}',
            is_private,
            subject_tag,
            owner_id,
        )

    def generate_unique_room_code(self) -> str:
        while True:
            code = str(random.randint(100000, 999999))
            if not self._room_model.get_room_by_code(code):
                return code
