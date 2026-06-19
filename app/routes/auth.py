from flask import Blueprint
from app.controllers.auth import AuthController


class AuthRoutes:
    def __init__(self):
        self.bp = Blueprint('auth', __name__)
        self.controller = AuthController()

    def register(self):
        self.bp.route('/login', methods=['GET', 'POST'])(self.controller.login)
        self.bp.route('/register', methods=['POST'])(self.controller.register)
        self.bp.route('/reset_password')(self.controller.reset_password)
        self.bp.route('/reset_password/send_code', methods=['POST'])(self.controller.send_reset_code)
        self.bp.route('/reset_password/verify', methods=['POST'])(self.controller.verify_reset_code)
        self.bp.route('/reset_password/set', methods=['POST'])(self.controller.set_new_password)
        self.bp.route('/logout')(self.controller.logout)
        self.bp.route('/keepalive', methods=['POST'])(self.controller.keepalive)
        return self.bp


# Expose a module-level `bp` for compatibility with existing imports
bp = AuthRoutes().register()
