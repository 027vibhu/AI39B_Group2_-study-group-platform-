"""Unit tests for app.models.database: users functions, Database wrapper, cascade.

The users functions use ``get_database_connection()`` directly with a
``with connection.cursor() as cursor`` block, so we patch that factory.
"""

import unittest
from unittest.mock import patch

from tests.support import make_fake_connection, sql_of, params_of, find_call
import app.models.database as db_mod


class UsersFunctionsTest(unittest.TestCase):
    def _run(self, fn, *args, fetchone=None, fetchall=None, lastrowid=1, rowcount=1):
        conn, cursor = make_fake_connection(fetchone, fetchall, lastrowid, rowcount)
        with patch('app.models.database.get_database_connection', return_value=conn):
            result = fn(*args)
        conn.close.assert_called_once()
        return result, cursor

    def test_get_user_by_identifier(self):
        row = {'id': 1, 'username': 'alice'}
        result, cursor = self._run(db_mod.get_user_by_identifier, 'alice', fetchone=row)
        self.assertEqual(result, row)
        self.assertEqual(params_of(cursor.execute.call_args), ('alice', 'alice'))

    def test_get_user_by_email(self):
        result, cursor = self._run(db_mod.get_user_by_email, 'a@b.com', fetchone={'id': 1})
        self.assertIn('WHERE email = %s', sql_of(cursor.execute.call_args))
        self.assertEqual(params_of(cursor.execute.call_args), ('a@b.com',))

    def test_get_user_by_username(self):
        _, cursor = self._run(db_mod.get_user_by_username, 'alice', fetchone={'id': 1})
        self.assertIn('WHERE username = %s', sql_of(cursor.execute.call_args))

    def test_get_user_by_id(self):
        _, cursor = self._run(db_mod.get_user_by_id, 5, fetchone={'id': 5})
        self.assertEqual(params_of(cursor.execute.call_args), (5,))

    def test_deactivate_user(self):
        _, cursor = self._run(db_mod.deactivate_user, 5)
        self.assertIn('is_active = 0', sql_of(cursor.execute.call_args))
        self.assertEqual(params_of(cursor.execute.call_args), (5,))

    def test_reactivate_user(self):
        _, cursor = self._run(db_mod.reactivate_user, 5)
        self.assertIn('is_active = 1', sql_of(cursor.execute.call_args))

    def test_update_user_password_by_email(self):
        result, cursor = self._run(db_mod.update_user_password_by_email, 'a@b.com', 'HASH', rowcount=1)
        self.assertEqual(result, 1)
        self.assertEqual(params_of(cursor.execute.call_args), ('HASH', 'a@b.com'))

    def test_update_user_profile(self):
        _, cursor = self._run(db_mod.update_user_profile, 1, 'F', 'L', 'Sch', 'Addr', 'Bio')
        self.assertEqual(params_of(cursor.execute.call_args), ('F', 'L', 'Sch', 'Addr', 'Bio', 1))

    def test_set_user_role(self):
        _, cursor = self._run(db_mod.set_user_role, 1, 'admin')
        self.assertEqual(params_of(cursor.execute.call_args), ('admin', 1))

    def test_get_all_users(self):
        result, cursor = self._run(db_mod.get_all_users, fetchall=[{'id': 1}, {'id': 2}])
        self.assertEqual(len(result), 2)
        self.assertIn('ORDER BY created_at DESC', sql_of(cursor.execute.call_args))


class CreateUserTest(unittest.TestCase):
    @patch('app.models.database.create_users_table')
    def test_create_user_returns_lastrowid(self, mock_create_table):
        conn, cursor = make_fake_connection(lastrowid=99)
        with patch('app.models.database.get_database_connection', return_value=conn):
            new_id = db_mod.create_user('alice', 'a@b.com', 'HASH')
        self.assertEqual(new_id, 99)
        self.assertEqual(params_of(cursor.execute.call_args), ('alice', 'a@b.com', 'HASH'))


class DeleteUserCascadeTest(unittest.TestCase):
    def test_delete_user_cascades(self):
        conn, cursor = make_fake_connection(rowcount=1)
        # No owned rooms / notes -> fetchall returns [] for the SELECT loops.
        cursor.fetchall.return_value = []
        with patch('app.models.database.get_database_connection', return_value=conn):
            db_mod.delete_user(5)
        # The user row deletion runs last.
        self.assertIsNotNone(find_call(cursor.execute, 'DELETE FROM users WHERE id = %s'))
        self.assertIsNotNone(find_call(cursor.execute, 'DELETE FROM user_room WHERE user_id = %s'))
        conn.close.assert_called_once()


class DatabaseWrapperTest(unittest.TestCase):
    def _wrapper(self, fetchone=None, fetchall=None, lastrowid=7, rowcount=3):
        conn, cursor = make_fake_connection(fetchone, fetchall, lastrowid, rowcount)
        with patch('app.models.database.get_database_connection', return_value=conn):
            wrapper = db_mod.Database()
        return wrapper, cursor

    def test_fetch_one(self):
        wrapper, cursor = self._wrapper(fetchone={'id': 1})
        self.assertEqual(wrapper.fetch_one('SELECT 1', ()), {'id': 1})

    def test_fetch_all(self):
        wrapper, cursor = self._wrapper(fetchall=[{'id': 1}])
        self.assertEqual(wrapper.fetch_all('SELECT 1'), [{'id': 1}])

    def test_execute_returns_lastrowid(self):
        wrapper, cursor = self._wrapper(lastrowid=7)
        self.assertEqual(wrapper.execute('INSERT ...', ()), 7)

    def test_close(self):
        wrapper, cursor = self._wrapper()
        wrapper.close()  # should not raise


if __name__ == '__main__':
    unittest.main()
