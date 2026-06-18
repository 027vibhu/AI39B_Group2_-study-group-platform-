from flask import Blueprint
from app.controllers.deactivated_account_controller import DeactivatedAccountController


class AccountRoutes:
    def __init__(self):
        self.bp = Blueprint('account', __name__)
        self.controller = DeactivatedAccountController()

    def register(self):
        self.bp.route('/profile/deactivate', methods=['POST'])(self.controller.deactivate_account)
        return self.bp


bp = AccountRoutes().register()
