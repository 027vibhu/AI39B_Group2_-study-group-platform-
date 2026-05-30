# app/routes/RoomRoutes.py
from flask import Blueprint, jsonify
from app.controllers.room_controller import RoomController

# Creating the blueprint to hook into the application routing structure
room_bp = Blueprint('room_routes', __name__)

class RoomRoutesAPI:
    @staticmethod
    @room_bp.route('/api/rooms/public', methods=['GET'])
    def get_public_rooms():
        """Backend endpoint returning a clean list of public room objects."""
        controller = RoomController()
        try:
            # Execute business logic layer to get list of Domain objects
            public_rooms = controller.browse_public_rooms()
            
            # Serialize the domain objects using their built-in OOP methods
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