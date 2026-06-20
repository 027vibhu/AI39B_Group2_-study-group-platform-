"""Unit tests for BaseModel helpers.

BaseModel imports ``Database`` lazily inside each method, so patching
``app.models.database.Database`` intercepts every call.
"""

import unittest

from tests.support import patch_database, sql_of, params_of
from app.models.base_model import BaseModel


class Widget(BaseModel):
    @property
    def table(self):
        return 'widgets'


class TestBaseModel(unittest.TestCase):
    def test_find_by_id(self):
        with patch_database(fetch_one={'id': 3}) as db:
            result = Widget().find_by_id(3)
        self.assertEqual(result, {'id': 3})
        self.assertIn('FROM widgets WHERE id = %s', sql_of(db.fetch_one.call_args))
        self.assertEqual(params_of(db.fetch_one.call_args), (3,))
        db.close.assert_called_once()

    def test_find_by(self):
        with patch_database(fetch_one={'id': 1, 'name': 'x'}) as db:
            Widget().find_by('name', 'x')
        self.assertIn('WHERE name = %s', sql_of(db.fetch_one.call_args))
        self.assertEqual(params_of(db.fetch_one.call_args), ('x',))

    def test_find_all_default_order(self):
        with patch_database(fetch_all=[{'id': 1}, {'id': 2}]) as db:
            rows = Widget().find_all()
        self.assertEqual(len(rows), 2)
        self.assertIn('ORDER BY id', sql_of(db.fetch_all.call_args))

    def test_count_all_returns_total(self):
        with patch_database(fetch_one={'total': 7}) as db:
            self.assertEqual(Widget().count_all(), 7)

    def test_count_all_no_row_returns_zero(self):
        with patch_database(fetch_one=None):
            self.assertEqual(Widget().count_all(), 0)

    def test_execute_passthrough(self):
        with patch_database(execute=42) as db:
            self.assertEqual(Widget().execute('DELETE FROM widgets', ()), 42)
            db.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
