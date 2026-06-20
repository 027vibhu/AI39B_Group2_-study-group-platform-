"""Unit tests for the exam_countdown model (module-level helpers)."""

import unittest
from unittest.mock import patch

from tests.support import make_fake_db, params_of, find_call
import app.models.exam_countdown as ec


class ExamCountdownTestBase(unittest.TestCase):
    def setUp(self):
        p = patch('app.models.exam_countdown.ensure_database_exists')
        p.start()
        self.addCleanup(p.stop)
        self.db = make_fake_db()
        p2 = patch('app.models.database.Database', return_value=self.db)
        p2.start()
        self.addCleanup(p2.stop)


class TestCreateExam(ExamCountdownTestBase):
    def test_insert_params(self):
        self.db.execute.return_value = 7
        new_id = ec.create_exam('Finals', '2026-07-01 09:00', 'hard', 1, '#fff')
        self.assertEqual(new_id, 7)
        insert = find_call(self.db.execute, 'INSERT INTO exam_countdown')
        self.assertEqual(params_of(insert), ('Finals', '2026-07-01 09:00', 'hard', '#fff', 1))


class TestGetExams(ExamCountdownTestBase):
    def test_query(self):
        self.db.fetch_all.return_value = [{'id': 1}]
        rows = ec.get_exams_for_user(1)
        self.assertEqual(rows, [{'id': 1}])
        self.assertEqual(params_of(self.db.fetch_all.call_args), (1,))


if __name__ == '__main__':
    unittest.main()
