import random

from app.controllers.base_controller import BaseController
from app.models.room import RoomModel


class RoomController(BaseController):
    def __init__(self):
        super().__init__()

    def create_room(self, room_name: str, subject_tag: str, submitted_code: str, is_private: bool):
        submitted_code = (submitted_code or '').strip().upper()
        if len(submitted_code) == 6 and submitted_code.isalnum() and not RoomModel.get_room_by_code(submitted_code):
            code = submitted_code
        else:
            code = self._generate_unique_room_code()

        return RoomModel.create_room(
            code,
            room_name or f'Room {code}',
            subject_tag,
            is_private,
        )

    def _generate_unique_room_code(self) -> str:
        while True:
            code = str(random.randint(100000, 999999))
            if not get_room_by_code(code):
                return code
