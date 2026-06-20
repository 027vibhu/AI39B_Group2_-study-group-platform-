"""Unit tests for RoomController (RoomModel patched)."""

import unittest
from unittest.mock import patch

from tests.support import make_controller_app
from tests.support.fixtures import room_row


class RoomControllerTestBase(unittest.TestCase):
    def setUp(self):
        self.app = make_controller_app()
        self.model_patcher = patch('app.controllers.room_controller.RoomModel')
        self.RoomModel = self.model_patcher.start()
        self.addCleanup(self.model_patcher.stop)
        self.model = self.RoomModel.return_value
        from app.controllers.room_controller import RoomController
        self.controller = RoomController()


class TestBrowsePublicRooms(RoomControllerTestBase):
    def test_returns_public_rooms(self):
        self.model.get_all_public_rooms.return_value = [room_row()]
        result = self.controller.browse_public_rooms()
        self.assertEqual(len(result), 1)
        self.model.create_table.assert_called_once()


class TestCreateRoom(RoomControllerTestBase):
    def test_uses_valid_submitted_code(self):
        self.model.get_room_by_code.return_value = None
        self.model.create_room.return_value = room_row(code='ABC123')
        self.controller.create_room('My Room', 'math', 'abc123', False, owner_id=1)
        # submitted code is upper-cased and reused
        self.assertEqual(self.model.create_room.call_args.args[0], 'ABC123')

    def test_generates_code_when_submitted_invalid(self):
        # invalid (too short) -> falls back to generate_unique_room_code
        self.model.get_room_by_code.return_value = None
        self.model.create_room.return_value = room_row()
        self.controller.create_room('My Room', 'math', 'xy', False, owner_id=1)
        code = self.model.create_room.call_args.args[0]
        self.assertEqual(len(code), 6)
        self.assertTrue(code.isdigit())

    def test_generates_code_when_submitted_taken(self):
        # taken submitted code -> generate a fresh one (None on 2nd+ lookup)
        self.model.get_room_by_code.side_effect = [room_row(), None]
        self.model.create_room.return_value = room_row()
        self.controller.create_room('My Room', 'math', 'TAKEN1', False, owner_id=1)
        code = self.model.create_room.call_args.args[0]
        self.assertEqual(len(code), 6)


class TestGenerateUniqueCode(RoomControllerTestBase):
    def test_retries_until_unused(self):
        self.model.get_room_by_code.side_effect = [room_row(), room_row(), None]
        code = self.controller.generate_unique_room_code()
        self.assertEqual(len(code), 6)
        self.assertEqual(self.model.get_room_by_code.call_count, 3)


if __name__ == '__main__':
    unittest.main()
