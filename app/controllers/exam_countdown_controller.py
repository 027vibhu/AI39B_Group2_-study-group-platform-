from app.controllers.base_controller import BaseController
from app.models.exam_countdown import (
    ensure_table_exists,
    create_exam,
    get_exams_for_user,
)


class ExamCountdownController(BaseController):
    def __init__(self):
        # Ensure table exists on controller initialization
        ensure_table_exists()

    def list_exams(self, user_id=None):
        """Return a list of exams for the given user_id."""
        if user_id is None:
            user_id = self.get_current_user_id()
        return get_exams_for_user(user_id)

    def create_exam(self, title, exam_datetime, notes='', color=None, user_id=None):
        """Create a new exam countdown and return the new id."""
        if user_id is None:
            user_id = self.get_current_user_id()
        return create_exam(title, exam_datetime, notes, user_id, color)
