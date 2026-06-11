from flask import Blueprint, jsonify
from app.controllers.join_leave_notification_controller import JoinLeaveNotificationController


class JoinLeaveNotificationRoutes:
    def __init__(self):
        self.bp = Blueprint('join_leave_notification', __name__)

    def register(self):
        self.bp.route('/api/room/<int:room_id>/notifications', methods=['GET'])(self.get_room_notifications)
        return self.bp

    def get_room_notifications(self, room_id):
        controller = JoinLeaveNotificationController()
        try:
            notifications = controller.get_notifications(room_id)
            return jsonify({
                'status': 'success',
                'room_id': room_id,
                'notifications': notifications,
            }), 200
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Error fetching notifications: {str(e)}',
            }), 500


join_leave_notification_bp = JoinLeaveNotificationRoutes().register()
