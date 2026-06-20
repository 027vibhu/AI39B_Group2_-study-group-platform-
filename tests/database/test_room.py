"""Unit tests for RoomModel, including log_room_action ban/kick branches."""

import unittest
from datetime import datetime
from unittest.mock import patch

from tests.support import make_fake_db, sql_of, params_of, find_call
from tests.support.fixtures import room_row
from app.models.room import RoomModel


class RoomTestBase(unittest.TestCase):
    def setUp(self):
        p = patch('app.models.room.ensure_database_exists')
        p.start()
        self.addCleanup(p.stop)
        self.db = make_fake_db()
        p2 = patch('app.models.database.Database', return_value=self.db)
        p2.start()
        self.addCleanup(p2.stop)
        self.model = RoomModel()


class TestLookups(RoomTestBase):
    def test_get_room_by_code(self):
        self.db.fetch_one.return_value = room_row()
        result = self.model.get_room_by_code('ABC123')
        self.assertEqual(result['code'], 'ABC123')
        self.assertEqual(params_of(self.db.fetch_one.call_args), ('ABC123',))

    def test_is_user_in_room_true(self):
        self.db.fetch_one.return_value = {'1': 1}
        self.assertTrue(self.model.is_user_in_room(1, 10))

    def test_is_user_in_room_false(self):
        self.db.fetch_one.return_value = None
        self.assertFalse(self.model.is_user_in_room(1, 10))


class TestCreateRoom(RoomTestBase):
    def test_inserts_and_returns_row(self):
        self.db.execute.return_value = 10
        self.db.fetch_one.return_value = room_row(id=10)
        result = self.model.create_room('ABC123', 'Room', False, 'math', owner_id=1)
        insert = find_call(self.db.execute, 'INSERT INTO room')
        self.assertIsNotNone(insert)
        # is_private coerced to int
        self.assertEqual(params_of(insert), ('ABC123', 'Room', 0, 'math', 1))
        # owner membership recorded
        self.assertIsNotNone(find_call(self.db.execute, 'INSERT INTO user_room'))
        self.assertEqual(result['id'], 10)


class TestLogRoomAction(RoomTestBase):
    def test_ban_with_duration_sets_ban_until(self):
        self.model.log_room_action('bob', 'ABC123', 'Room', 'ban', duration_minutes=30)
        params = params_of(self.db.execute.call_args)
        self.assertIsInstance(params[4], datetime)  # ban_until

    def test_ban_without_duration_is_null(self):
        self.model.log_room_action('bob', 'ABC123', 'Room', 'ban')
        self.assertIsNone(params_of(self.db.execute.call_args)[4])

    def test_kick_has_no_ban_until(self):
        self.model.log_room_action('bob', 'ABC123', 'Room', 'kick', duration_minutes=30)
        self.assertIsNone(params_of(self.db.execute.call_args)[4])


class TestBanCheck(RoomTestBase):
    def test_banned_true(self):
        self.db.fetch_one.return_value = {'id': 1}
        self.assertTrue(self.model.is_user_banned_from_room('bob', 'ABC123'))

    def test_banned_false(self):
        self.db.fetch_one.return_value = None
        self.assertFalse(self.model.is_user_banned_from_room('bob', 'ABC123'))


class TestDeleteCascade(RoomTestBase):
    def test_delete_room_by_id_cascades(self):
        self.model.delete_room_by_id(10)
        self.assertIsNotNone(find_call(self.db.execute, 'DELETE FROM message WHERE room_id'))
        self.assertIsNotNone(find_call(self.db.execute, 'DELETE FROM user_room WHERE room_id'))
        self.assertIsNotNone(find_call(self.db.execute, 'DELETE FROM room WHERE id'))


if __name__ == '__main__':
    unittest.main()
