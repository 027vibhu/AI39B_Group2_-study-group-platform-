"""Route tests for the exam_countdown blueprint."""

import unittest
from unittest.mock import patch

from tests.routes.conftest_app import build_test_app
from tests.support.fixtures import login

EC = 'app.controllers.exam_countdown_controller'


class ExamCountdownRoutesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = build_test_app()

    def setUp(self):
        self.client = self.app.test_client()

    def test_requires_login(self):
        self.assertEqual(self.client.get('/exams').status_code, 302)

    @patch(f'{EC}.ensure_table_exists')
    @patch(f'{EC}.get_exams_for_user', return_value=[{'id': 1}])
    def test_list_exams(self, mock_get, mock_ensure):
        login(self.client)
        resp = self.client.get('/exams')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['exams'], [{'id': 1}])

    @patch(f'{EC}.ensure_table_exists')
    @patch(f'{EC}.create_exam', return_value=5)
    def test_create_exam(self, mock_create, mock_ensure):
        login(self.client)
        resp = self.client.post('/exams', json={'title': 'Finals', 'exam_datetime': '2026-07-01 09:00'})
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.get_json()['id'], 5)

    @patch(f'{EC}.ensure_table_exists')
    def test_create_exam_missing_fields_400(self, mock_ensure):
        login(self.client)
        resp = self.client.post('/exams', json={'title': 'Finals'})
        self.assertEqual(resp.status_code, 400)


if __name__ == '__main__':
    unittest.main()
