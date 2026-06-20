"""Unit tests for BrowseRoomsController (delegates to RoomController)."""

import unittest
from unittest.mock import patch

from tests.support import make_controller_app
from tests.support.fixtures import room_row


class TestBrowseRooms(unittest.TestCase):
    def setUp(self):
        self.app = make_controller_app()
        from app.controllers.browse_rooms_controller import BrowseRoomsController
        self.controller = BrowseRoomsController()

    @patch('app.controllers.browse_rooms_controller.BaseController.render', return_value='page')
    @patch('app.controllers.browse_rooms_controller.RoomController')
    def test_renders_with_rooms(self, mock_room_controller, mock_render):
        mock_room_controller.return_value.browse_public_rooms.return_value = [room_row(), room_row()]
        with self.app.test_request_context():
            result = self.controller.show_browse_rooms()
        self.assertEqual(result, 'page')
        kwargs = mock_render.call_args.kwargs
        self.assertEqual(kwargs['room_count'], 2)
        self.assertEqual(len(kwargs['rooms']), 2)

    @patch('app.controllers.browse_rooms_controller.BaseController.render', return_value='page')
    @patch('app.controllers.browse_rooms_controller.RoomController')
    def test_handles_no_rooms(self, mock_room_controller, mock_render):
        mock_room_controller.return_value.browse_public_rooms.return_value = None
        with self.app.test_request_context():
            self.controller.show_browse_rooms()
        self.assertEqual(mock_render.call_args.kwargs['room_count'], 0)


if __name__ == '__main__':
    unittest.main()
