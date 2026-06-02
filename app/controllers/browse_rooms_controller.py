from app.controllers.base_controller import BaseController
from app.controllers.room_controller import RoomController


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
        # Reuse RoomController to avoid duplicate room lookup logic
        public_rooms = RoomController().browse_public_rooms()

        # Prepare context data
        context = {
            'rooms': public_rooms if public_rooms else [],
            'room_count': len(public_rooms) if public_rooms else 0
        }

        # Render template with rooms data
        return self.render('browse_rooms.html', **context)
