"""Route tests for the auth blueprint via the Flask test client."""

import unittest
from unittest.mock import patch

from tests.routes.conftest_app import build_test_app
from tests.support.fixtures import login, user_row


class AuthRoutesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = build_test_app()

    def setUp(self):
        self.client = self.app.test_client()

    def test_login_get_is_public_200(self):
        self.assertEqual(self.client.get('/login').status_code, 200)

    @patch('app.controllers.auth.get_user_by_identifier', return_value=None)
    def test_login_post_bad_credentials_401(self, mock_lookup):
        resp = self.client.post('/login', data={'identifier': 'x', 'password': 'secret1'})
        self.assertEqual(resp.status_code, 401)

    @patch('app.controllers.auth.check_password_hash', return_value=True)
    @patch('app.controllers.auth.get_user_by_identifier')
    def test_login_post_success_redirects(self, mock_lookup, mock_check):
        mock_lookup.return_value = user_row()
        resp = self.client.post('/login', data={'identifier': 'alice', 'password': 'secret1'})
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/dashboard', resp.headers['Location'])

    def test_logout_redirects_to_login(self):
        login(self.client)
        resp = self.client.get('/logout')
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/login', resp.headers['Location'])

    def test_reset_password_page_public(self):
        self.assertEqual(self.client.get('/reset_password').status_code, 200)


if __name__ == '__main__':
    unittest.main()
