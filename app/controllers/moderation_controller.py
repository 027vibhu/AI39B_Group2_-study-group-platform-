
from app.controllers.base_controller import BaseController
from app.models.database import get_user_by_id


class ModerationController(BaseController):
    """Controller for moderation page actions.

    Provides a method to render the moderation view and passes the
    currently logged-in user (if any) to the template.
    """

    def show_moderation(self):
        user_id = self.get_session_user_id()
        current_user = get_user_by_id(user_id) if user_id else None
        return self.render('moderation.html', current_user=current_user)
