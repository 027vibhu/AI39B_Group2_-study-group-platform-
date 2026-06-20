"""Unit tests for the Task model, including dynamic UPDATE SET-clause branches.

Task classmethods do ``from app.models.database import Database`` inside the
method (patched at the source) and call ``ensure_table_exists`` ->
``create_tasks_table`` (patched to a no-op).
"""

import unittest
from unittest.mock import patch

from tests.support import make_fake_db, sql_of, params_of
from app.models.task import Task


class TaskTestBase(unittest.TestCase):
    def setUp(self):
        # Neutralise table creation.
        p = patch('app.models.task.create_tasks_table')
        p.start()
        self.addCleanup(p.stop)
        # Fake the Database used inside each classmethod.
        self.db = make_fake_db()
        p2 = patch('app.models.database.Database', return_value=self.db)
        p2.start()
        self.addCleanup(p2.stop)


class TestCreate(TaskTestBase):
    def test_insert_params(self):
        self.db.execute.return_value = 7
        new_id = Task.create(1, 'Read', status='done', priority='high', due_date='2026-06-01', description='d')
        self.assertEqual(new_id, 7)
        params = params_of(self.db.execute.call_args)
        # (user_id, title, description, status, priority, due_date, is_done)
        self.assertEqual(params[0], 1)
        self.assertEqual(params[3], 'done')
        self.assertEqual(params[4], 'high')
        self.assertEqual(params[6], 1)  # is_done derived from status == 'done'

    def test_invalid_status_and_priority_default(self):
        Task.create(1, 'Read', status='weird', priority='urgent')
        params = params_of(self.db.execute.call_args)
        self.assertEqual(params[3], 'todo')
        self.assertEqual(params[4], 'medium')
        self.assertEqual(params[6], 0)


class TestFindForUser(TaskTestBase):
    def test_query(self):
        self.db.fetch_all.return_value = [{'id': 1}]
        rows = Task.find_for_user(1, limit=10)
        self.assertEqual(rows, [{'id': 1}])
        self.assertEqual(params_of(self.db.fetch_all.call_args), (1, 10))


class TestToggle(TaskTestBase):
    def test_returns_new_state(self):
        self.db.fetch_one.return_value = {'is_done': 1}
        self.assertEqual(Task.toggle(7, 1), 1)

    def test_missing_returns_none(self):
        self.db.fetch_one.return_value = None
        self.assertIsNone(Task.toggle(7, 1))


class TestUpdate(TaskTestBase):
    def test_no_fields_returns_none_without_db(self):
        self.assertIsNone(Task.update(7, 1))
        self.db.execute.assert_not_called()

    def test_title_only(self):
        self.db.fetch_one.return_value = {'id': 7, 'title': 'New'}
        Task.update(7, 1, title='New')
        sql = sql_of(self.db.execute.call_args)
        self.assertIn('title = %s', sql)
        self.assertNotIn('status = %s', sql)

    def test_status_also_sets_is_done(self):
        self.db.fetch_one.return_value = {'id': 7}
        Task.update(7, 1, status='done')
        sql = sql_of(self.db.execute.call_args)
        self.assertIn('status = %s', sql)
        self.assertIn('is_done = %s', sql)

    def test_combination_builds_multiple_clauses(self):
        self.db.fetch_one.return_value = {'id': 7}
        Task.update(7, 1, title='T', priority='low', due_date='2026-01-01')
        sql = sql_of(self.db.execute.call_args)
        self.assertIn('title = %s', sql)
        self.assertIn('priority = %s', sql)
        self.assertIn('due_date = %s', sql)
        # params end with (task_id, user_id)
        self.assertEqual(params_of(self.db.execute.call_args)[-2:], (7, 1))


class TestDelete(TaskTestBase):
    def test_delete(self):
        self.db.execute.return_value = 1
        Task.delete(7, 1)
        self.assertIn('DELETE FROM dashboard_tasks', sql_of(self.db.execute.call_args))
        self.assertEqual(params_of(self.db.execute.call_args), (7, 1))


if __name__ == '__main__':
    unittest.main()
