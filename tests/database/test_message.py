"""Unit tests for the MessageModel (incl. time_label derivation)."""

import unittest
from datetime import datetime
from unittest.mock import patch

from tests.support import make_fake_db, sql_of, params_of, find_call
from app.models.message import MessageModel
import app.models.message as message_mod


class MessageTestBase(unittest.TestCase):
    def setUp(self):
        p = patch('app.models.message.ensure_database_exists')
        p.start()
        self.addCleanup(p.stop)
        self.db = make_fake_db()
        p2 = patch('app.models.database.Database', return_value=self.db)
        p2.start()
        self.addCleanup(p2.stop)
        self.model = MessageModel()


class TestCreateMessage(MessageTestBase):
    def test_insert(self):
        self.db.execute.return_value = 3
        new_id = self.model.create_message(10, 'alice', 'hello')
        self.assertEqual(new_id, 3)
        insert = find_call(self.db.execute, 'INSERT INTO message')
        self.assertEqual(params_of(insert), (10, 'alice', 'hello'))


class TestGetMessages(MessageTestBase):
    def test_adds_time_label_from_datetime(self):
        self.db.fetch_all.return_value = [
            {'id': 1, 'timestamp': datetime(2026, 6, 1, 9, 5)},
            {'id': 2, 'timestamp': None},
        ]
        rows = self.model.get_messages_for_room(10)
        self.assertTrue(rows[0]['time_label'])      # formatted
        self.assertEqual(rows[1]['time_label'], '')  # no timestamp -> empty

    def test_delete_message(self):
        self.model.delete_message(3)
        self.assertIn('DELETE FROM message', sql_of(self.db.execute.call_args))
        self.assertEqual(params_of(self.db.execute.call_args), (3,))


class TestModuleLevelGetById(MessageTestBase):
    def test_get_message_by_id_adds_time_label(self):
        self.db.fetch_one.return_value = {'id': 3, 'timestamp': datetime(2026, 6, 1, 9, 5)}
        msg = message_mod.get_message_by_id(3)
        self.assertIn('time_label', msg)


if __name__ == '__main__':
    unittest.main()
