from flask import request, session
from app.controllers.base_controller import BaseController
from app.models.deactivated_account import deactivate_account
from app.models.database import get_user_by_id


class DeactivatedAccountController(BaseController):
    def __init__(self):
        super().__init__()

    def deactivate_account(self):
        user_id = self.get_current_user_id()
        if not user_id:
            return self.redirect('auth.login')

        current_user = get_user_by_id(user_id)
        if not current_user:
            session.clear()
            return self.redirect('auth.login')

        reason = (request.form.get('deactivation_reason') or '').strip() or None
        deactivate_account(user_id, reason)

        session.clear()
        return self.flash_and_redirect(
            'Your account has been deactivated. Please contact support to restore access.',
            'success',
            'auth.login',
        )
