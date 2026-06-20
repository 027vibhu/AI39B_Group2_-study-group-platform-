"""Unit tests for the WhiteboardModel."""

import unittest
from unittest.mock import patch

from tests.support import make_fake_db, params_of, find_call
from app.models.whiteboard import WhiteboardModel


class WhiteboardTestBase(unittest.TestCase):
    def setUp(self):
        p = patch('app.models.whiteboard.ensure_database_exists')
        p.start()
        self.addCleanup(p.stop)
        self.db = make_fake_db()
        p2 = patch('app.models.database.Database', return_value=self.db)
        p2.start()
        self.addCleanup(p2.stop)
        self.model = WhiteboardModel()


class TestBoardCrud(WhiteboardTestBase):
    def test_create_whiteboard_returns_row(self):
        self.db.execute.return_value = 5
        self.db.fetch_one.return_value = {'id': 5, 'code': 'ABC123'}
        result = self.model.create_whiteboard('ABC123', 'Board', owner_id=1)
        insert = find_call(self.db.execute, 'INSERT INTO whiteboard ')
        self.assertEqual(params_of(insert), ('ABC123', 'Board', 1))
        self.assertEqual(result['id'], 5)

    def test_get_by_code(self):
        self.db.fetch_one.return_value = {'id': 5}
        self.model.get_whiteboard_by_code('ABC123')
        self.assertEqual(params_of(self.db.fetch_one.call_args), ('ABC123',))

    def test_is_user_in_whiteboard(self):
        self.db.fetch_one.return_value = {'1': 1}
        self.assertTrue(self.model.is_user_in_whiteboard(1, 5))
        self.db.fetch_one.return_value = None
        self.assertFalse(self.model.is_user_in_whiteboard(1, 5))


class TestState(WhiteboardTestBase):
    def test_save_state_upsert_and_touch(self):
        self.model.save_state(5, '{"shapes": []}', 1, 'alice')
        self.assertIsNotNone(find_call(self.db.execute, 'INSERT INTO whiteboard_state'))
        self.assertIsNotNone(find_call(self.db.execute, 'UPDATE whiteboard SET updated_at'))

    def test_clear_state(self):
        self.model.clear_state(5)
        delete = find_call(self.db.execute, 'DELETE FROM whiteboard_state')
        self.assertEqual(params_of(delete), (5,))


if __name__ == '__main__':
    unittest.main()
