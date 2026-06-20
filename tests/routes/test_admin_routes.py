"""Route tests for the admin blueprint (@admin_required gating)."""

import unittest
from unittest.mock import patch

from tests.routes.conftest_app import build_test_app
from tests.support.fixtures import login, room_row


class AdminRoutesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = build_test_app()

    def setUp(self):
        self.client = self.app.test_client()

    def test_anonymous_redirected_to_login(self):
        resp = self.client.get('/admin/')
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/login', resp.headers['Location'])

    def test_non_admin_redirected_to_login(self):
        login(self.client, role='user')
        resp = self.client.get('/admin/')
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/login', resp.headers['Location'])

    @patch('app.controllers.admin_controller.get_messages_for_room', return_value=[])
    @patch('app.controllers.admin_controller.get_all_users', return_value=[])
    @patch('app.controllers.admin_controller.get_all_rooms', return_value=[])
    def test_admin_can_reach_dashboard(self, mock_rooms, mock_users, mock_msgs):
        login(self.client, role='admin')
        with patch('app.controllers.admin_controller.AdminController.dashboard',
                   return_value='admin_ok'):
            resp = self.client.get('/admin/')
        self.assertEqual(resp.status_code, 200)

    @patch('app.controllers.admin_controller.delete_room_by_id')
    @patch('app.controllers.admin_controller.get_room_by_id', return_value=room_row())
    def test_admin_delete_room(self, mock_get, mock_delete):
        login(self.client, role='admin')
        resp = self.client.post('/admin/rooms/10/delete')
        self.assertEqual(resp.status_code, 302)
        mock_delete.assert_called_once_with(10)


if __name__ == '__main__':
    unittest.main()
