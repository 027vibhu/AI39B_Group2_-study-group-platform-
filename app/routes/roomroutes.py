# app/routes/RoomRoutes.py
from flask import Blueprint, jsonify
from app.controllers.room_controller import RoomController


class RoomRoutes:
    def __init__(self):
        self.bp = Blueprint('room_routes', __name__)

    def register(self):
        self.bp.route('/api/rooms/public', methods=['GET'])(self.get_public_rooms)
        return self.bp

    def get_public_rooms(self):
        """Backend endpoint returning a clean list of public room objects."""
        controller = RoomController()
        try:
            public_rooms = controller.browse_public_rooms()
            serialized_data = [room.to_dict() if hasattr(room, 'to_dict') else room for room in public_rooms]
            return jsonify({
                "status": "success",
                "count": len(serialized_data),
                "rooms": serialized_data
            }), 200
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"An error occurred while fetching public rooms: {str(e)}"
            }), 500


# Expose room_bp for compatibility with imports elsewhere
room_bp = RoomRoutes().register()