# app/controllers/room_controller.py
from app.models import room as room_repository

class RoomController:
    def __init__(self):
        pass

    def browse_public_rooms(self):
        """
        Fetches public room records and maps them 
        into instances of the Room object.
        """
        # Fetch raw records from your newly added model helper function
        raw_rooms = room_repository.get_all_public_rooms()
        
        # Instantiate Room objects out of the raw records (Pure OOP tracking)
        room_objects = []
        for r in raw_rooms:
            room_obj = room_repository.Room(
                room_id=r['id'],
                code=r['code'],
                name=r['name'],
                is_private=r['is_private'],
                created_at=r['created_at']
            )
            room_objects.append(room_obj)
            
        return room_objects