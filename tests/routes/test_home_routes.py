"""Route tests for the home blueprint: the login gate + a few endpoints."""

import unittest
from unittest.mock import patch

from tests.routes.conftest_app import build_test_app
from tests.support.fixtures import login

XHR = {'X-Requested-With': 'XMLHttpRequest'}


class LoginGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = build_test_app()

    def setUp(self):
        self.client = self.app.test_client()

    def test_public_pages_reachable_logged_out(self):
        for path in ('/', '/features', '/about'):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 200)

    def test_protected_page_redirects_logged_out(self):
        for path in ('/dashboard', '/notes', '/schedule', '/profile'):
            with self.subTest(path=path):
                resp = self.client.get(path)
                self.assertEqual(resp.status_code, 302)
                self.assertIn('/login', resp.headers['Location'])


class TaskRouteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = build_test_app()

    def setUp(self):
        self.client = self.app.test_client()

    def test_create_requires_login(self):
        # AJAX request without a session -> gate redirects to login.
        resp = self.client.post('/tasks/create', data={'title': 'x'}, headers=XHR)
        self.assertEqual(resp.status_code, 302)

    @patch('app.controllers.task_controller.Task')
    def test_create_task_success(self, MockTask):
        MockTask.create.return_value = 7
        login(self.client)
        resp = self.client.post('/tasks/create',
                                data={'title': 'Read', 'status': 'todo'}, headers=XHR)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.get_json()['status'], 'success')

    @patch('app.controllers.task_controller.Task')
    def test_delete_task_success(self, MockTask):
        login(self.client)
        resp = self.client.post('/tasks/7/delete', headers=XHR)
        self.assertEqual(resp.status_code, 200)
        MockTask.delete.assert_called_once_with(7, 1)


if __name__ == '__main__':
    unittest.main()
