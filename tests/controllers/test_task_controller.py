"""Unit tests for TaskController (model-class style: patch the ``Task`` class)."""

import unittest
from unittest.mock import patch

from flask import session

from tests.support import make_controller_app
from tests.support.fixtures import task_row

# The controller reads form fields (request.form) but chooses a JSON response
# when the request carries this header. So "ajax" requests are form data + header.
XHR = {'X-Requested-With': 'XMLHttpRequest'}


class TaskControllerTestBase(unittest.TestCase):
    def setUp(self):
        self.app = make_controller_app()
        # Patch the Task class for the whole test: this also neutralises the
        # __init__ call to Task.ensure_table_exists().
        self.task_patcher = patch('app.controllers.task_controller.Task')
        self.Task = self.task_patcher.start()
        self.addCleanup(self.task_patcher.stop)
        from app.controllers.task_controller import TaskController
        self.controller = TaskController()


class TestCreateTask(TaskControllerTestBase):
    def test_requires_login_json(self):
        with self.app.test_request_context(method='POST', data={'title': 'x'}, headers=XHR):
            resp, status = self.controller.create_task()
        self.assertEqual(status, 401)

    def test_requires_login_form_redirects(self):
        with self.app.test_request_context(method='POST', data={'title': 'x'}):
            response = self.controller.create_task()
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login', response.location)

    def test_empty_title_json_400(self):
        with self.app.test_request_context(method='POST', data={'title': '   '}, headers=XHR):
            session['user_id'] = 1
            resp, status = self.controller.create_task()
        self.assertEqual(status, 400)
        self.Task.create.assert_not_called()

    def test_success_json_201(self):
        self.Task.create.return_value = 7
        with self.app.test_request_context(
            method='POST', data={'title': 'Read', 'status': 'todo', 'priority': 'high'}, headers=XHR
        ):
            session['user_id'] = 1
            resp, status = self.controller.create_task()
        self.assertEqual(status, 201)
        body = resp.get_json()
        self.assertEqual(body['status'], 'success')
        self.assertEqual(body['task']['id'], 7)
        self.assertEqual(body['task']['priority'], 'high')
        self.Task.create.assert_called_once()

    def test_success_form_redirects(self):
        self.Task.create.return_value = 7
        with self.app.test_request_context(method='POST', data={'title': 'Read'}):
            session['user_id'] = 1
            response = self.controller.create_task()
        self.assertEqual(response.status_code, 302)
        self.assertIn('/home/schedule', response.location)


class TestUpdateTask(TaskControllerTestBase):
    def test_not_found_json_404(self):
        self.Task.update.return_value = None
        with self.app.test_request_context(method='POST', data={'status': 'done'}, headers=XHR):
            session['user_id'] = 1
            resp, status = self.controller.update_task(7)
        self.assertEqual(status, 404)

    def test_success_json(self):
        self.Task.update.return_value = task_row(status='done', is_done=1)
        with self.app.test_request_context(method='POST', data={'status': 'done'}, headers=XHR):
            session['user_id'] = 1
            resp, status = self.controller.update_task(7)
        self.assertEqual(status, 200)
        self.assertEqual(resp.get_json()['task']['status'], 'done')


class TestToggleTask(TaskControllerTestBase):
    def test_not_found_404(self):
        self.Task.toggle.return_value = None
        with self.app.test_request_context(method='POST', headers=XHR):
            session['user_id'] = 1
            resp, status = self.controller.toggle_task(7)
        self.assertEqual(status, 404)

    def test_success(self):
        self.Task.toggle.return_value = 1
        with self.app.test_request_context(method='POST', headers=XHR):
            session['user_id'] = 1
            resp, status = self.controller.toggle_task(7)
        self.assertEqual(status, 200)
        self.assertEqual(resp.get_json()['is_done'], 1)


class TestDeleteTask(TaskControllerTestBase):
    def test_success_json(self):
        with self.app.test_request_context(method='POST', headers=XHR):
            session['user_id'] = 1
            resp, status = self.controller.delete_task(7)
        self.assertEqual(status, 200)
        self.Task.delete.assert_called_once_with(7, 1)

    def test_requires_login(self):
        with self.app.test_request_context(method='POST', headers=XHR):
            resp, status = self.controller.delete_task(7)
        self.assertEqual(status, 401)


class TestWantsJson(TaskControllerTestBase):
    def test_xhr_header(self):
        with self.app.test_request_context(headers={'X-Requested-With': 'XMLHttpRequest'}):
            self.assertTrue(self.controller._wants_json())

    def test_plain_form_is_not_json(self):
        with self.app.test_request_context(method='POST', data={'a': 'b'}):
            self.assertFalse(self.controller._wants_json())


if __name__ == '__main__':
    unittest.main()
