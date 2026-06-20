"""Unit tests for ExamCountdownController (module functions patched)."""

import unittest
from unittest.mock import patch

from flask import session

from tests.support import make_controller_app

EC = 'app.controllers.exam_countdown_controller'


class ExamCountdownTestBase(unittest.TestCase):
    def setUp(self):
        self.app = make_controller_app()
        # Neutralise __init__ ensure_table_exists().
        self.patcher = patch(f'{EC}.ensure_table_exists')
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        from app.controllers.exam_countdown_controller import ExamCountdownController
        self.controller = ExamCountdownController()


class TestListExams(ExamCountdownTestBase):
    @patch(f'{EC}.get_exams_for_user', return_value=[{'id': 1}])
    def test_explicit_user_id(self, mock_get):
        result = self.controller.list_exams(user_id=5)
        self.assertEqual(result, [{'id': 1}])
        mock_get.assert_called_once_with(5)

    @patch(f'{EC}.get_exams_for_user', return_value=[])
    def test_defaults_to_session_user(self, mock_get):
        with self.app.test_request_context():
            session['user_id'] = 9
            self.controller.list_exams()
        mock_get.assert_called_once_with(9)


class TestCreateExam(ExamCountdownTestBase):
    @patch(f'{EC}.create_exam', return_value=42)
    def test_create_with_session_user(self, mock_create):
        with self.app.test_request_context():
            session['user_id'] = 9
            new_id = self.controller.create_exam('Finals', '2026-07-01 09:00', notes='hard', color='#fff')
        self.assertEqual(new_id, 42)
        mock_create.assert_called_once_with('Finals', '2026-07-01 09:00', 'hard', 9, '#fff')


if __name__ == '__main__':
    unittest.main()
