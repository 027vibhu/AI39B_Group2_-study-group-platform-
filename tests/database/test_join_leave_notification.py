"""Unit tests for the JoinLeaveNotificationModel."""

import unittest
from unittest.mock import patch

from tests.support import make_fake_db, params_of, find_call
from app.models.join_leave_notification import JoinLeaveNotificationModel


class JoinLeaveTestBase(unittest.TestCase):
    def setUp(self):
        p = patch('app.models.join_leave_notification.ensure_database_exists')
        p.start()
        self.addCleanup(p.stop)
        self.db = make_fake_db()
        p2 = patch('app.models.database.Database', return_value=self.db)
        p2.start()
        self.addCleanup(p2.stop)
        self.model = JoinLeaveNotificationModel()


class TestNotifications(JoinLeaveTestBase):
    def test_add_notification(self):
        self.db.execute.return_value = 4
        new_id = self.model.add_notification(10, 1, 'alice', 'join', 'hello')
        self.assertEqual(new_id, 4)
        insert = find_call(self.db.execute, 'INSERT INTO join_leave_notifications')
        self.assertEqual(params_of(insert), (10, 1, 'alice', 'join', 'hello'))

    def test_get_room_notifications(self):
        self.db.fetch_all.return_value = [{'id': 1}]
        rows = self.model.get_room_notifications(10, limit=25)
        self.assertEqual(rows, [{'id': 1}])
        self.assertEqual(params_of(self.db.fetch_all.call_args), (10, 25))


if __name__ == '__main__':
    unittest.main()
