"""Unit tests for the Flashcard model."""

import unittest
from unittest.mock import patch

from tests.support import make_fake_db, patch_database, sql_of, params_of, find_call
from app.models.flashcard import Flashcard


class FlashcardInstanceTest(unittest.TestCase):
    def test_create_set(self):
        with patch_database(execute=99) as db:
            self.assertEqual(Flashcard().create_set(5, 1, 'Title', 10), 99)
            self.assertEqual(params_of(db.execute.call_args), (5, 1, 'Title', 10))

    def test_create_flashcard(self):
        with patch_database(execute=1) as db:
            Flashcard().create_flashcard(5, 1, 'Q', 'A', set_id=99)
        self.assertEqual(params_of(db.execute.call_args), (99, 5, 1, 'Q', 'A'))

    def test_get_flashcards_for_set(self):
        with patch_database(fetch_all=[{'id': 1}]) as db:
            rows = Flashcard().get_flashcards_for_set(99)
        self.assertEqual(rows, [{'id': 1}])
        self.assertEqual(params_of(db.fetch_all.call_args), (99,))

    def test_count_for_note(self):
        with patch_database(fetch_one={'total': 4}):
            self.assertEqual(Flashcard().count_for_note(5), 4)

    def test_delete_flashcards_for_note(self):
        with patch_database(execute=1) as db:
            Flashcard().delete_flashcards_for_note(5)
        self.assertIsNotNone(find_call(db.execute, 'DELETE FROM flashcard_sets WHERE note_id'))
        self.assertIsNotNone(find_call(db.execute, 'DELETE FROM flashcards WHERE note_id'))


class FlashcardStaticTableTest(unittest.TestCase):
    @patch('app.models.flashcard.ensure_database_exists')
    @patch('app.models.flashcard.Database')
    def test_create_flashcards_table(self, MockDB, mock_ensure):
        db = make_fake_db()
        MockDB.return_value = db
        Flashcard.create_flashcards_table()
        self.assertIsNotNone(find_call(db.execute, 'CREATE TABLE IF NOT EXISTS flashcard_sets'))
        self.assertIsNotNone(find_call(db.execute, 'CREATE TABLE IF NOT EXISTS flashcards'))
        db.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
