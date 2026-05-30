from app.controllers.base_controller import BaseController
from app.models.subject_tag import SubjectTagModel
from app.models.room import RoomModel


class SubjectTagController(BaseController):
    """Controller for managing subject tags and room tag associations."""

    def __init__(self):
        super().__init__()
        self.tag_model = SubjectTagModel()

    def get_all_available_tags(self):
        """
        Retrieve all available subject tags in the system.
        
        Returns:
            list: List of all subject tags with their metadata.
        """
        return SubjectTagModel.get_all_tags()

    def get_room_tags(self, room_id):
        """
        Get all subject tags assigned to a specific room.
        
        Args:
            room_id (int): The ID of the room.
        
        Returns:
            list: List of tags associated with the room.
        """
        # Verify room exists
        room = RoomModel.get_room_by_id(room_id)
        if not room:
            return {"error": "Room not found", "status": 404}
        
        tags = SubjectTagModel.get_room_tags(room_id)
        return tags

    def add_tag_to_room(self, room_id, tag_name):
        """
        Add a subject tag to a room.
        
        Args:
            room_id (int): The ID of the room.
            tag_name (str): The name of the tag to add.
        
        Returns:
            dict: Status response with success/error information.
        """
        # Validate inputs
        if not room_id or not tag_name:
            return {"error": "Room ID and tag name are required", "status": 400}
        
        # Verify room exists
        room = RoomModel.get_room_by_id(room_id)
        if not room:
            return {"error": "Room not found", "status": 404}
        
        # Sanitize tag name
        tag_name = tag_name.strip().lower()
        
        if len(tag_name) == 0 or len(tag_name) > 100:
            return {"error": "Tag name must be between 1 and 100 characters", "status": 400}
        
        try:
            SubjectTagModel.add_tag_to_room(room_id, tag_name)
            return {"message": f"Tag '{tag_name}' added to room successfully", "status": 200}
        except Exception as e:
            return {"error": f"Failed to add tag: {str(e)}", "status": 500}

    def remove_tag_from_room(self, room_id, tag_id):
        """
        Remove a subject tag from a room.
        
        Args:
            room_id (int): The ID of the room.
            tag_id (int): The ID of the tag to remove.
        
        Returns:
            dict: Status response with success/error information.
        """
        # Validate inputs
        if not room_id or not tag_id:
            return {"error": "Room ID and tag ID are required", "status": 400}
        
        # Verify room exists
        room = RoomModel.get_room_by_id(room_id)
        if not room:
            return {"error": "Room not found", "status": 404}
        
        # Verify tag is assigned to room
        tags = SubjectTagModel.get_room_tags(room_id)
        tag_exists = any(tag['id'] == tag_id for tag in tags)
        
        if not tag_exists:
            return {"error": "Tag is not assigned to this room", "status": 404}
        
        try:
            SubjectTagModel.remove_tag_from_room(room_id, tag_id)
            return {"message": "Tag removed from room successfully", "status": 200}
        except Exception as e:
            return {"error": f"Failed to remove tag: {str(e)}", "status": 500}

    def bulk_add_tags_to_room(self, room_id, tag_names):
        """
        Add multiple subject tags to a room at once.
        
        Args:
            room_id (int): The ID of the room.
            tag_names (list): List of tag names to add.
        
        Returns:
            dict: Status response with success/error information and results.
        """
        # Validate inputs
        if not room_id or not tag_names:
            return {"error": "Room ID and tag names are required", "status": 400}
        
        if not isinstance(tag_names, list):
            return {"error": "Tag names must be a list", "status": 400}
        
        # Verify room exists
        room = RoomModel.get_room_by_id(room_id)
        if not room:
            return {"error": "Room not found", "status": 404}
        
        results = {"added": [], "failed": []}
        
        for tag_name in tag_names:
            tag_name = tag_name.strip().lower()
            
            if len(tag_name) == 0 or len(tag_name) > 100:
                results["failed"].append({
                    "tag": tag_name,
                    "reason": "Tag name must be between 1 and 100 characters"
                })
                continue
            
            try:
                SubjectTagModel.add_tag_to_room(room_id, tag_name)
                results["added"].append(tag_name)
            except Exception as e:
                results["failed"].append({
                    "tag": tag_name,
                    "reason": str(e)
                })
        
        return {
            "message": f"Added {len(results['added'])} tags",
            "results": results,
            "status": 200
        }

    def get_room_with_tags(self, room_id):
        """
        Get complete room information including all assigned tags.
        
        Args:
            room_id (int): The ID of the room.
        
        Returns:
            dict: Room data with associated tags.
        """
        # Get room info
        room = RoomModel.get_room_by_id(room_id)
        if not room:
            return {"error": "Room not found", "status": 404}
        
        # Get tags for the room
        tags = SubjectTagModel.get_room_tags(room_id)
        
        return {
            "room": room,
            "tags": tags,
            "status": 200
        }
