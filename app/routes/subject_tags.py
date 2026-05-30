from flask import Blueprint, request, session, jsonify
from app.controllers.subject_tag_controller import SubjectTagController

bp = Blueprint('subject_tags', __name__, url_prefix='/api')


@bp.before_request
def check_auth():
    """Ensure user is authenticated before accessing tag endpoints."""
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized - Please login first"}), 401


@bp.route('/tags', methods=['GET'])
def get_all_tags():
    """
    Get all available subject tags in the system.
    
    Returns:
        JSON: List of all subject tags
    """
    try:
        controller = SubjectTagController()
        tags = controller.get_all_available_tags()
        return jsonify({"tags": tags, "status": 200}), 200
    except Exception as e:
        return jsonify({"error": str(e), "status": 500}), 500


@bp.route('/rooms/<int:room_id>/tags', methods=['GET'])
def get_room_tags(room_id):
    """
    Get all subject tags assigned to a specific room.
    
    Args:
        room_id (int): The ID of the room
    
    Returns:
        JSON: List of tags for the room
    """
    try:
        controller = SubjectTagController()
        result = controller.get_room_tags(room_id)
        
        if isinstance(result, dict) and "error" in result:
            return jsonify(result), result.get("status", 500)
        
        return jsonify({"tags": result, "status": 200}), 200
    except Exception as e:
        return jsonify({"error": str(e), "status": 500}), 500


@bp.route('/rooms/<int:room_id>/tags', methods=['POST'])
def add_tag_to_room(room_id):
    """
    Add a subject tag to a room.
    
    Request JSON:
        {
            "tag_name": "Mathematics"
        }
    
    Returns:
        JSON: Status response
    """
    try:
        data = request.get_json()
        
        if not data or 'tag_name' not in data:
            return jsonify({
                "error": "Tag name is required",
                "status": 400
            }), 400
        
        tag_name = data.get('tag_name')
        
        controller = SubjectTagController()
        result = controller.add_tag_to_room(room_id, tag_name)
        
        return jsonify(result), result.get("status", 500)
    except Exception as e:
        return jsonify({"error": str(e), "status": 500}), 500


@bp.route('/rooms/<int:room_id>/tags/<int:tag_id>', methods=['DELETE'])
def remove_tag_from_room(room_id, tag_id):
    """
    Remove a subject tag from a room.
    
    Args:
        room_id (int): The ID of the room
        tag_id (int): The ID of the tag to remove
    
    Returns:
        JSON: Status response
    """
    try:
        controller = SubjectTagController()
        result = controller.remove_tag_from_room(room_id, tag_id)
        
        return jsonify(result), result.get("status", 500)
    except Exception as e:
        return jsonify({"error": str(e), "status": 500}), 500


@bp.route('/rooms/<int:room_id>/tags/bulk', methods=['POST'])
def bulk_add_tags(room_id):
    """
    Add multiple subject tags to a room at once.
    
    Request JSON:
        {
            "tag_names": ["Mathematics", "Science", "History"]
        }
    
    Returns:
        JSON: Status response with results
    """
    try:
        data = request.get_json()
        
        if not data or 'tag_names' not in data:
            return jsonify({
                "error": "Tag names list is required",
                "status": 400
            }), 400
        
        tag_names = data.get('tag_names')
        
        if not isinstance(tag_names, list):
            return jsonify({
                "error": "Tag names must be a list",
                "status": 400
            }), 400
        
        controller = SubjectTagController()
        result = controller.bulk_add_tags_to_room(room_id, tag_names)
        
        return jsonify(result), result.get("status", 500)
    except Exception as e:
        return jsonify({"error": str(e), "status": 500}), 500


@bp.route('/rooms/<int:room_id>/with-tags', methods=['GET'])
def get_room_with_tags(room_id):
    """
    Get complete room information including all assigned tags.
    
    Args:
        room_id (int): The ID of the room
    
    Returns:
        JSON: Room data with associated tags
    """
    try:
        controller = SubjectTagController()
        result = controller.get_room_with_tags(room_id)
        
        if isinstance(result, dict) and "error" in result:
            return jsonify(result), result.get("status", 500)
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e), "status": 500}), 500
