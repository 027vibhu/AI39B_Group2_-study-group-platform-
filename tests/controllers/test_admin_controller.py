"""Unit tests for AdminController (module functions + Note class + os.remove)."""

import unittest
from unittest.mock import patch

from flask import session

from tests.support import make_controller_app
from tests.support.fixtures import room_row, user_row, note_row, message_row


class AdminControllerTestBase(unittest.TestCase):
    def setUp(self):
        self.app = make_controller_app()
        self.note_patcher = patch('app.controllers.admin_controller.Note')
        self.Note = self.note_patcher.start()
        self.addCleanup(self.note_patcher.stop)
        self.note_model = self.Note.return_value
        from app.controllers.admin_controller import AdminController
        self.controller = AdminController()


class TestDashboard(AdminControllerTestBase):
    @patch('app.controllers.admin_controller.get_messages_for_room', return_value=[message_row()])
    @patch('app.controllers.admin_controller.get_all_users', return_value=[user_row()])
    @patch('app.controllers.admin_controller.get_all_rooms', return_value=[room_row()])
    @patch('app.controllers.admin_controller.render_template', return_value='admin_page')
    def test_dashboard_aggregates(self, mock_render, mock_rooms, mock_users, mock_msgs):
        self.note_model.get_all_notes.return_value = [note_row()]
        with self.app.test_request_context():
            result = self.controller.dashboard()
        self.assertEqual(result, 'admin_page')
        kwargs = mock_render.call_args.kwargs
        self.assertEqual(len(kwargs['rooms']), 1)
        self.assertEqual(len(kwargs['rooms_with_messages']), 1)


class TestDeleteRoom(AdminControllerTestBase):
    @patch('app.controllers.admin_controller.get_room_by_id', return_value=None)
    def test_missing_room(self, mock_get):
        with self.app.test_request_context():
            response = self.controller.delete_room(10)
        self.assertEqual(response.status_code, 302)

    @patch('app.controllers.admin_controller.delete_room_by_id')
    @patch('app.controllers.admin_controller.get_room_by_id', return_value=room_row())
    def test_deletes(self, mock_get, mock_delete):
        with self.app.test_request_context():
            self.controller.delete_room(10)
        mock_delete.assert_called_once_with(10)


class TestDeleteUser(AdminControllerTestBase):
    def test_cannot_delete_self(self):
        with self.app.test_request_context():
            session['user_id'] = 1
            response = self.controller.delete_user(1)
        self.assertEqual(response.status_code, 302)

    @patch('app.controllers.admin_controller.delete_user')
    @patch('app.controllers.admin_controller.get_user_by_id', return_value=user_row(id=2))
    def test_deletes_other_user(self, mock_get, mock_delete):
        with self.app.test_request_context():
            session['user_id'] = 1
            self.controller.delete_user(2)
        mock_delete.assert_called_once_with(2)


class TestDeleteMessage(AdminControllerTestBase):
    @patch('app.controllers.admin_controller.get_message_by_id', return_value=None)
    def test_missing_message(self, mock_get):
        with self.app.test_request_context():
            response = self.controller.delete_message(3)
        self.assertEqual(response.status_code, 302)

    @patch('app.controllers.admin_controller.delete_message')
    @patch('app.controllers.admin_controller.get_message_by_id', return_value=message_row())
    def test_deletes(self, mock_get, mock_delete):
        with self.app.test_request_context():
            self.controller.delete_message(3)
        mock_delete.assert_called_once_with(3)


class TestDeleteNote(AdminControllerTestBase):
    @patch('app.controllers.admin_controller.os.remove')
    def test_deletes_and_removes_file(self, mock_remove):
        self.note_model.get_note_by_id.return_value = note_row(pdf_url='uploads/notes/x.pdf')
        with self.app.test_request_context():
            self.controller.delete_note(5)
        self.note_model.delete_note.assert_called_once_with(5)


if __name__ == '__main__':
    unittest.main()
