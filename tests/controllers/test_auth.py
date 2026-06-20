"""Unit tests for AuthController against the *real* current API.

The real controller uses module-level DB functions (patched at
``app.controllers.auth.*``), returns ``render_template(..., login_error=...)``
with HTTP status codes, and sets ``session['username']`` (not ``user_name``).
"""

import unittest
from unittest.mock import patch

from flask import session

from tests.support import make_controller_app
from tests.support.fixtures import user_row
from app.controllers.auth import AuthController


class AuthTestBase(unittest.TestCase):
    def setUp(self):
        self.app = make_controller_app()
        self.controller = AuthController()


# --------------------------------------------------------------------------- #
#  LOGIN
# --------------------------------------------------------------------------- #
class TestLogin(AuthTestBase):
    @patch('app.controllers.auth.render_template')
    def test_get_shows_form(self, mock_render):
        mock_render.return_value = 'login_page'
        with self.app.test_request_context(method='GET'):
            result = self.controller.login()
        self.assertEqual(result, 'login_page')
        mock_render.assert_called_once_with('login.html', active_form='sign-in')

    @patch('app.controllers.auth.render_template')
    def test_missing_fields_returns_400(self, mock_render):
        mock_render.return_value = 'page'
        with self.app.test_request_context(method='POST', data={'identifier': '', 'password': ''}):
            body, status = self.controller.login()
        self.assertEqual(status, 400)

    @patch('app.controllers.auth.get_user_by_identifier', return_value=None)
    @patch('app.controllers.auth.render_template', return_value='page')
    def test_unknown_user_returns_401(self, mock_render, mock_lookup):
        with self.app.test_request_context(method='POST',
                                           data={'identifier': 'nope', 'password': 'secret1'}):
            body, status = self.controller.login()
        self.assertEqual(status, 401)
        mock_lookup.assert_called_once_with('nope')

    @patch('app.controllers.auth.check_password_hash', return_value=False)
    @patch('app.controllers.auth.get_user_by_identifier')
    @patch('app.controllers.auth.render_template', return_value='page')
    def test_wrong_password_returns_401_no_session(self, mock_render, mock_lookup, mock_check):
        mock_lookup.return_value = user_row()
        with self.app.test_request_context(method='POST',
                                           data={'identifier': 'alice', 'password': 'wrong'}):
            body, status = self.controller.login()
            self.assertEqual(status, 401)
            self.assertNotIn('user_id', session)

    @patch('app.controllers.auth.check_password_hash', return_value=True)
    @patch('app.controllers.auth.get_user_by_identifier')
    def test_success_sets_session_and_redirects(self, mock_lookup, mock_check):
        mock_lookup.return_value = user_row(id=2, username='bob', role='user')
        with self.app.test_request_context(method='POST',
                                           data={'identifier': 'bob', 'password': 'secret1'}):
            response = self.controller.login()
            self.assertEqual(session['user_id'], 2)
            self.assertEqual(session['username'], 'bob')
            self.assertEqual(session['role'], 'user')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/home/dashboard', response.location)

    def test_already_logged_in_redirects(self):
        with self.app.test_request_context(method='GET'):
            session['user_id'] = 9
            response = self.controller.login()
        self.assertEqual(response.status_code, 302)
        self.assertIn('/home/dashboard', response.location)

    @patch('app.controllers.auth.send_reactivation_code', return_value=(True, None))
    @patch('app.controllers.auth.check_password_hash', return_value=True)
    @patch('app.controllers.auth.get_user_by_identifier')
    def test_deactivated_account_starts_reactivation(self, mock_lookup, mock_check, mock_send):
        mock_lookup.return_value = user_row(is_active=0)
        with self.app.test_request_context(method='POST',
                                           data={'identifier': 'alice', 'password': 'secret1'}):
            response = self.controller.login()
            self.assertIn('reactivate_user_id', session)
            self.assertNotIn('user_id', session)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/reactivate', response.location)
        mock_send.assert_called_once()


# --------------------------------------------------------------------------- #
#  REGISTER
# --------------------------------------------------------------------------- #
class TestRegister(AuthTestBase):
    @patch('app.controllers.auth.render_template', return_value='page')
    def test_missing_fields_400(self, mock_render):
        with self.app.test_request_context(method='POST',
                                           data={'username': '', 'email': '', 'password': ''}):
            _, status = self.controller.register()
        self.assertEqual(status, 400)

    @patch('app.controllers.auth.render_template', return_value='page')
    def test_short_username_400(self, mock_render):
        with self.app.test_request_context(method='POST',
                                           data={'username': 'ab', 'email': 'a@b.com', 'password': 'secret1'}):
            _, status = self.controller.register()
        self.assertEqual(status, 400)

    @patch('app.controllers.auth.render_template', return_value='page')
    def test_bad_email_400(self, mock_render):
        with self.app.test_request_context(method='POST',
                                           data={'username': 'alice', 'email': 'bad', 'password': 'secret1'}):
            _, status = self.controller.register()
        self.assertEqual(status, 400)

    @patch('app.controllers.auth.render_template', return_value='page')
    def test_short_password_400(self, mock_render):
        with self.app.test_request_context(method='POST',
                                           data={'username': 'alice', 'email': 'a@b.com', 'password': '123'}):
            _, status = self.controller.register()
        self.assertEqual(status, 400)

    @patch('app.controllers.auth.get_user_by_username', return_value=user_row())
    @patch('app.controllers.auth.render_template', return_value='page')
    def test_duplicate_username_409(self, mock_render, mock_uname):
        with self.app.test_request_context(method='POST',
                                           data={'username': 'alice', 'email': 'a@b.com', 'password': 'secret1'}):
            _, status = self.controller.register()
        self.assertEqual(status, 409)

    @patch('app.controllers.auth.get_user_by_email', return_value=user_row())
    @patch('app.controllers.auth.get_user_by_username', return_value=None)
    @patch('app.controllers.auth.render_template', return_value='page')
    def test_duplicate_email_409(self, mock_render, mock_uname, mock_email):
        with self.app.test_request_context(method='POST',
                                           data={'username': 'alice', 'email': 'a@b.com', 'password': 'secret1'}):
            _, status = self.controller.register()
        self.assertEqual(status, 409)

    @patch('app.controllers.auth.create_user', return_value=42)
    @patch('app.controllers.auth.get_user_by_email', return_value=None)
    @patch('app.controllers.auth.get_user_by_username', return_value=None)
    def test_success_creates_user_and_redirects(self, mock_uname, mock_email, mock_create):
        with self.app.test_request_context(method='POST',
                                           data={'username': 'alice', 'email': 'Alice@B.com', 'password': 'secret1'}):
            response = self.controller.register()
            self.assertEqual(session['user_id'], 42)
            self.assertEqual(session['username'], 'alice')
        mock_create.assert_called_once()
        # email is lower-cased before storage
        self.assertEqual(mock_create.call_args.args[1], 'alice@b.com')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/home/profile', response.location)


# --------------------------------------------------------------------------- #
#  PASSWORD RESET (JSON endpoints)
# --------------------------------------------------------------------------- #
class TestPasswordReset(AuthTestBase):
    @patch('app.controllers.auth.get_user_by_email', return_value=None)
    def test_send_code_bad_email_400(self, mock_email):
        with self.app.test_request_context(method='POST', data={'email': 'bad'}):
            resp, status = self.controller.send_reset_code()
        self.assertEqual(status, 400)
        self.assertFalse(resp.get_json()['ok'])

    @patch('app.controllers.auth.get_user_by_email', return_value=None)
    def test_send_code_unknown_email_404(self, mock_email):
        with self.app.test_request_context(method='POST', data={'email': 'a@b.com'}):
            resp, status = self.controller.send_reset_code()
        self.assertEqual(status, 404)

    @patch('app.controllers.auth.send_reset_code', return_value=(True, None))
    @patch('app.controllers.auth.get_user_by_email', return_value=user_row())
    def test_send_code_success(self, mock_email, mock_send):
        with self.app.test_request_context(method='POST', data={'email': 'a@b.com'}):
            resp, status = self.controller.send_reset_code()
            self.assertEqual(status, 200)
            self.assertTrue(resp.get_json()['ok'])
            self.assertEqual(session['reset_email'], 'a@b.com')
        mock_send.assert_called_once()

    def test_verify_code_matches(self):
        with self.app.test_request_context(method='POST', data={'code': '123456'}):
            session['reset_code'] = '123456'
            session['reset_expires'] = 9_999_999_999
            resp, status = self.controller.verify_reset_code()
            self.assertEqual(status, 200)
            self.assertTrue(session['reset_verified'])

    def test_verify_code_wrong(self):
        with self.app.test_request_context(method='POST', data={'code': '000000'}):
            session['reset_code'] = '123456'
            session['reset_expires'] = 9_999_999_999
            resp, status = self.controller.verify_reset_code()
        self.assertEqual(status, 400)

    @patch('app.controllers.auth.update_user_password_by_email', return_value=1)
    def test_set_new_password_requires_verification(self, mock_update):
        with self.app.test_request_context(method='POST', data={'password': 'secret1', 'confirm': 'secret1'}):
            resp, status = self.controller.set_new_password()
        self.assertEqual(status, 403)
        mock_update.assert_not_called()

    @patch('app.controllers.auth.update_user_password_by_email', return_value=1)
    def test_set_new_password_success(self, mock_update):
        with self.app.test_request_context(method='POST', data={'password': 'secret1', 'confirm': 'secret1'}):
            session['reset_verified'] = True
            session['reset_email'] = 'a@b.com'
            session['reset_expires'] = 9_999_999_999
            resp, status = self.controller.set_new_password()
            self.assertEqual(status, 200)
            self.assertNotIn('reset_verified', session)
        mock_update.assert_called_once()


# --------------------------------------------------------------------------- #
#  DEACTIVATE / REACTIVATE / LOGOUT
# --------------------------------------------------------------------------- #
class TestAccountLifecycle(AuthTestBase):
    @patch('app.controllers.auth.deactivate_user')
    @patch('app.controllers.auth.check_password_hash', return_value=True)
    @patch('app.controllers.auth.get_user_by_id')
    @patch('app.controllers.auth.render_template', return_value='login_notice_page')
    def test_deactivate_success_clears_session(self, mock_render, mock_get, mock_check, mock_deact):
        mock_get.return_value = user_row(role='user')
        with self.app.test_request_context(method='POST', data={'password': 'secret1'}):
            session['user_id'] = 1
            result = self.controller.deactivate_account()
            self.assertNotIn('user_id', session)
        mock_deact.assert_called_once_with(1)
        self.assertEqual(result, 'login_notice_page')

    @patch('app.controllers.auth.get_user_by_id')
    def test_admin_cannot_deactivate(self, mock_get):
        mock_get.return_value = user_row(role='admin')
        with self.app.test_request_context(method='POST', data={'password': 'secret1'}):
            session['user_id'] = 1
            response = self.controller.deactivate_account()
        self.assertEqual(response.status_code, 302)
        self.assertIn('/home/profile', response.location)

    @patch('app.controllers.auth.get_user_by_id')
    @patch('app.controllers.auth.reactivate_user')
    def test_reactivate_verify_signs_in(self, mock_react, mock_get):
        mock_get.return_value = user_row(id=3, username='carol')
        with self.app.test_request_context(method='POST', data={'code': '111111'}):
            session['reactivate_user_id'] = 3
            session['reactivate_code'] = '111111'
            session['reactivate_expires'] = 9_999_999_999
            resp, status = self.controller.reactivate_verify()
            self.assertEqual(status, 200)
            self.assertEqual(session['user_id'], 3)
            self.assertNotIn('reactivate_user_id', session)
        mock_react.assert_called_once_with(3)

    def test_logout_clears_session(self):
        with self.app.test_request_context():
            session['user_id'] = 1
            session['username'] = 'alice'
            response = self.controller.logout()
            self.assertNotIn('user_id', session)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login', response.location)


if __name__ == '__main__':
    unittest.main()
