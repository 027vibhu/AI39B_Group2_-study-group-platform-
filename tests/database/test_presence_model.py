"""Unit tests for the RoomPresenceModel."""

import unittest
from unittest.mock import patch

from tests.support import make_fake_db, params_of, find_call
from app.models.presence_model import RoomPresenceModel


class PresenceTestBase(unittest.TestCase):
    def setUp(self):
        p = patch('app.models.presence_model.ensure_database_exists')
        p.start()
        self.addCleanup(p.stop)
        self.db = make_fake_db()
        p2 = patch('app.models.database.Database', return_value=self.db)
        p2.start()
        self.addCleanup(p2.stop)
        self.model = RoomPresenceModel()


class TestPresence(PresenceTestBase):
    def test_set_user_online_upsert(self):
        self.model.set_user_online(1, 10, 'alice')
        insert = find_call(self.db.execute, 'INSERT INTO room_presence')
        # (user_id, room_id, username, status, username, status)
        self.assertEqual(params_of(insert), (1, 10, 'alice', 'online', 'alice', 'online'))

    def test_set_user_offline_status(self):
        self.model.set_user_offline(1, 10, 'alice')
        insert = find_call(self.db.execute, 'INSERT INTO room_presence')
        self.assertEqual(params_of(insert)[3], 'offline')

    def test_get_online_users(self):
        self.db.fetch_all.return_value = [{'user_id': 1}]
        rows = self.model.get_online_users(10)
        self.assertEqual(rows, [{'user_id': 1}])
        self.assertEqual(params_of(self.db.fetch_all.call_args), (10,))


if __name__ == '__main__':
    unittest.main()
