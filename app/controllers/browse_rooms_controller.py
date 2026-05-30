from app.controllers.base_controller import BaseController
from app.models.room_model import RoomModel


class BrowseRoomsController(BaseController):
    """
    Controller for handling browse rooms functionality.
    Inherits from BaseController to use helper methods like render().
    """

    def show_browse_rooms(self):
        """
        Fetch all public rooms and render the browse_rooms template.

        Returns:
            Rendered template with public rooms data
        """
        # Ensure the room table exists before querying
        room_model = RoomModel()
        room_model.create_table()
        public_rooms = room_model.get_all_public_rooms()

        # Prepare context data
        context = {
            'rooms': public_rooms if public_rooms else [],
            'room_count': len(public_rooms) if public_rooms else 0
        }

        # Render template with rooms data
        return self.render('browse_rooms.html', **context)
