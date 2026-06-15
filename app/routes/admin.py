from flask import Blueprint
from app.controllers.admin_controller import AdminController
from app.auth import admin_required


class AdminRoutes:
    def __init__(self):
        self.bp = Blueprint('admin', __name__, url_prefix='/admin')
        self.controller = AdminController()

    def register(self):
        self.bp.route('/')(admin_required(self.controller.dashboard))
        self.bp.route('/rooms/<int:room_id>/delete', methods=['POST'])(admin_required(self.controller.delete_room))
        self.bp.route('/notes/<int:note_id>/delete', methods=['POST'])(admin_required(self.controller.delete_note))
        self.bp.route('/users/<int:user_id>/delete', methods=['POST'])(admin_required(self.controller.delete_user))
        self.bp.route('/messages/<int:message_id>/delete', methods=['POST'])(admin_required(self.controller.delete_message))
        return self.bp


bp = AdminRoutes().register()
