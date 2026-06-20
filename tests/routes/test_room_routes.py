"""Route tests for the room_routes blueprint (/api/rooms/public)."""

import unittest
from unittest.mock import patch

from tests.routes.conftest_app import build_test_app
from tests.support.fixtures import login, room_row


class RoomRoutesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = build_test_app()

    def setUp(self):
        self.client = self.app.test_client()

    def test_requires_login(self):
        self.assertEqual(self.client.get('/api/rooms/public').status_code, 302)

    @patch('app.controllers.room_controller.RoomModel')
    def test_returns_public_rooms(self, MockRoomModel):
        MockRoomModel.return_value.get_all_public_rooms.return_value = [room_row(), room_row()]
        login(self.client)
        resp = self.client.get('/api/rooms/public')
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertEqual(body['status'], 'success')
        self.assertEqual(body['count'], 2)


if __name__ == '__main__':
    unittest.main()
