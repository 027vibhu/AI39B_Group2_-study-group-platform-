"""Unit tests for the SharedFileModel."""

import unittest
from unittest.mock import patch

from tests.support import make_fake_db, params_of, find_call
from app.models.shared_file import SharedFileModel


class SharedFileTestBase(unittest.TestCase):
    def setUp(self):
        p = patch('app.models.shared_file.ensure_database_exists')
        p.start()
        self.addCleanup(p.stop)
        self.db = make_fake_db()
        p2 = patch('app.models.database.Database', return_value=self.db)
        p2.start()
        self.addCleanup(p2.stop)
        self.model = SharedFileModel()


class TestSharedFile(SharedFileTestBase):
    def test_create_shared_file(self):
        self.db.execute.return_value = 12
        new_id = self.model.create_shared_file(10, 'alice', 'orig.pdf', 'stored.pdf', 'application/pdf', 2048)
        self.assertEqual(new_id, 12)
        insert = find_call(self.db.execute, 'INSERT INTO shared_file')
        self.assertEqual(params_of(insert), (10, 'alice', 'orig.pdf', 'stored.pdf', 'application/pdf', 2048))

    def test_get_shared_file_by_id(self):
        self.db.fetch_one.return_value = {'id': 12}
        self.assertEqual(self.model.get_shared_file_by_id(12)['id'], 12)
        self.assertEqual(params_of(self.db.fetch_one.call_args), (12,))

    def test_get_shared_files_for_room(self):
        self.db.fetch_all.return_value = [{'id': 1}, {'id': 2}]
        rows = self.model.get_shared_files_for_room(10)
        self.assertEqual(len(rows), 2)
        self.assertEqual(params_of(self.db.fetch_all.call_args), (10,))


if __name__ == '__main__':
    unittest.main()
