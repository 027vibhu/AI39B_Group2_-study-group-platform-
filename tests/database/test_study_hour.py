"""Unit tests for the StudyHour model."""

import unittest
from datetime import date
from unittest.mock import patch

from tests.support import make_fake_db, sql_of, params_of
from app.models.study_hour import StudyHour


class StudyHourTestBase(unittest.TestCase):
    def setUp(self):
        p = patch('app.models.study_hour.create_study_hours_table')
        p.start()
        self.addCleanup(p.stop)
        self.db = make_fake_db()
        p2 = patch('app.models.database.Database', return_value=self.db)
        p2.start()
        self.addCleanup(p2.stop)


class TestRecord(StudyHourTestBase):
    def test_insert(self):
        self.db.execute.return_value = 3
        new_id = StudyHour.record(1, date(2026, 6, 1), 90, 'notes')
        self.assertEqual(new_id, 3)
        self.assertIn('INSERT INTO study_hours', sql_of(self.db.execute.call_args))
        self.assertEqual(params_of(self.db.execute.call_args), (1, date(2026, 6, 1), 90, 'notes'))


class TestFindForUser(StudyHourTestBase):
    def test_query(self):
        self.db.fetch_all.return_value = [{'id': 1}]
        rows = StudyHour.find_for_user(1, limit=20)
        self.assertEqual(rows, [{'id': 1}])
        self.assertEqual(params_of(self.db.fetch_all.call_args), (1, 20))


if __name__ == '__main__':
    unittest.main()
