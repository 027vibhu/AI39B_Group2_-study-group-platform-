from flask import Blueprint, request
from app.controllers.user_status_controller import UserStatusController

# Create the Blueprint for this user story
user_status_bp = Blueprint('user_status', _name_)

@user_status_bp.route('/members/online', methods=['GET'])
def view_online_members():
    """
    Route to view the online members webpage.
    """
    controller = UserStatusController()
    return controller.get_online_status_page()

@user_status_bp.route('/api/status/update', methods=['POST'])
def update_member_status():
    """
    API Route allowing the application to change a user's status.
    Expects JSON data: {"user_id": 1, "is_online": true}
    """
    data = request.get_json() or {}
    user_id = data.get('user_id')
    is_online = data.get('is_online', False)
    
    controller = UserStatusController()
    return controller.update_status_api(user_id, is_online)