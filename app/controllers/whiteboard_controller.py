from app.controllers.base_controller import BaseController
from app.models.whiteboard import Whiteboard


class WhiteboardController(BaseController):
    def __init__(self):
        super().__init__()
        self.whiteboard_model = Whiteboard()
        self.whiteboard_model.ensure_table_exists()

    def save_whiteboard(self, room_id, title, drawing_data):
        user_id = self.get_current_user_id()
        if not user_id:
            return None

        return self.whiteboard_model.save_drawing(
            room_id,
            user_id,
            drawing_data,
            title or '',
        )

    def update_whiteboard(self, drawing_id, title, drawing_data):
        return self.whiteboard_model.update_drawing(
            drawing_id,
            drawing_data,
            title,
        )

    def get_room_whiteboards(self, room_id):
        return self.whiteboard_model.get_drawings_for_room(room_id)

    def get_whiteboard(self, drawing_id):
        return self.whiteboard_model.get_drawing_by_id(drawing_id)
