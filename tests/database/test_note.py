"""Unit tests for the Note model (instance SQL + static table helpers)."""

import unittest
from unittest.mock import patch

from tests.support import make_fake_db, patch_database, sql_of, params_of, find_call
from app.models.note import Note


class NoteInstanceTest(unittest.TestCase):
    def test_create_note(self):
        with patch_database(execute=5) as db:
            self.assertEqual(Note().create_note(1, 'T', 'u/p.pdf', 'desc'), 5)
            self.assertEqual(params_of(db.execute.call_args), (1, 'T', 'u/p.pdf', 'desc'))

    def test_get_notes_for_user(self):
        with patch_database(fetch_all=[{'id': 1}]) as db:
            rows = Note().get_notes_for_user(1)
        self.assertEqual(rows, [{'id': 1}])
        self.assertEqual(params_of(db.fetch_all.call_args), (1,))

    def test_share_note_insert_ignore(self):
        with patch_database(execute=1) as db:
            Note().share_note(5, 2, 1)
        self.assertIn('INSERT IGNORE INTO note_shares', sql_of(db.execute.call_args))
        self.assertEqual(params_of(db.execute.call_args), (5, 2, 1))

    def test_delete_note_cascades_shares_first(self):
        with patch_database(execute=1) as db:
            Note().delete_note(5)
        self.assertIsNotNone(find_call(db.execute, 'DELETE FROM note_shares WHERE note_id'))
        self.assertIsNotNone(find_call(db.execute, 'DELETE FROM notes WHERE id'))

    def test_set_content_text(self):
        with patch_database(execute=1) as db:
            Note().set_content_text(5, 'cached')
        self.assertEqual(params_of(db.execute.call_args), ('cached', 5))


class NoteStaticTableTest(unittest.TestCase):
    """Static methods use the module-level ``app.models.note.Database`` symbol."""

    @patch('app.models.note.ensure_database_exists')
    @patch('app.models.note.Database')
    def test_ensure_content_column_adds_when_missing(self, MockDB, mock_ensure):
        db = make_fake_db()
        MockDB.return_value = db
        # Column does NOT exist for either column -> ALTER runs twice.
        db.fetch_one.return_value = {'c': 0}
        Note.ensure_content_column()
        alters = [c for c in db.execute.call_args_list if 'ADD COLUMN' in c.args[0]]
        self.assertEqual(len(alters), 2)

    @patch('app.models.note.ensure_database_exists')
    @patch('app.models.note.Database')
    def test_ensure_content_column_skips_when_present(self, MockDB, mock_ensure):
        db = make_fake_db()
        MockDB.return_value = db
        db.fetch_one.return_value = {'c': 1}  # already present
        Note.ensure_content_column()
        alters = [c for c in db.execute.call_args_list if 'ADD COLUMN' in c.args[0]]
        self.assertEqual(len(alters), 0)


if __name__ == '__main__':
    unittest.main()
