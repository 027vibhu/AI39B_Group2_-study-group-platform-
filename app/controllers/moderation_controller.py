from app.controllers.base_controller import BaseController


class ModerationController(BaseController):
    """Controller for moderation page actions.

    Currently provides a method to render the moderation view. Additional
    moderation actions (ban/unban, remove message, etc.) will be added
    in subsequent steps following raw-SQL model implementations.
    """

    def show_moderation(self):
        user_id = self.get_session_user_id()
        # Future: load moderation-related data via models using raw SQL
        return self.render('moderation.html')
