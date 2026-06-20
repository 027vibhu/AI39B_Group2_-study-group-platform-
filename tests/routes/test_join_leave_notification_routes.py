"""Route tests for the join_leave_notification blueprint."""

import unittest
from unittest.mock import patch

from tests.routes.conftest_app import build_test_app
from tests.support.fixtures import login


class JoinLeaveRoutesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = build_test_app()

    def setUp(self):
        self.client = self.app.test_client()

    def test_requires_login(self):
        self.assertEqual(self.client.get('/api/room/10/notifications').status_code, 302)

    @patch('app.controllers.join_leave_notification_controller.'
           'JoinLeaveNotificationController.get_notifications', return_value=[{'id': 1}])
    def test_returns_notifications(self, mock_get):
        login(self.client)
        resp = self.client.get('/api/room/10/notifications')
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertEqual(body['status'], 'success')
        self.assertEqual(body['room_id'], 10)
        self.assertEqual(body['notifications'], [{'id': 1}])


if __name__ == '__main__':
    unittest.main()
