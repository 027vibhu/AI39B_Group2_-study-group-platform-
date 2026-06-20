"""Unit tests for NoteController (Note class + module functions + AI services)."""

import unittest
from unittest.mock import patch, MagicMock

from flask import session

from tests.support import make_controller_app
from tests.support.fixtures import note_row, user_row


class NoteControllerTestBase(unittest.TestCase):
    def setUp(self):
        self.app = make_controller_app()
        # Patch Note for the whole test -> neutralises __init__ table creation.
        self.note_patcher = patch('app.controllers.note_controller.Note')
        self.Note = self.note_patcher.start()
        self.addCleanup(self.note_patcher.stop)
        self.note_model = self.Note.return_value
        from app.controllers.note_controller import NoteController
        self.controller = NoteController()


class TestShareNote(NoteControllerTestBase):
    @patch('app.controllers.note_controller.get_user_by_username')
    def test_share_with_unknown_user_flashes_error(self, mock_lookup):
        self.note_model.get_note_by_id.return_value = note_row(user_id=1)
        mock_lookup.return_value = None
        with self.app.test_request_context(method='POST', data={'username': 'ghost'}):
            session['user_id'] = 1
            response = self.controller.share_note(5)
        self.assertEqual(response.status_code, 302)
        self.note_model.share_note.assert_not_called()

    @patch('app.controllers.note_controller.get_user_by_username')
    def test_share_success(self, mock_lookup):
        self.note_model.get_note_by_id.return_value = note_row(user_id=1)
        mock_lookup.return_value = user_row(id=2, username='bob')
        with self.app.test_request_context(method='POST', data={'username': 'bob'}):
            session['user_id'] = 1
            response = self.controller.share_note(5)
        self.assertEqual(response.status_code, 302)
        self.note_model.share_note.assert_called_once_with(5, 2, 1)

    def test_cannot_share_with_self(self):
        self.note_model.get_note_by_id.return_value = note_row(user_id=1)
        with patch('app.controllers.note_controller.get_user_by_username',
                   return_value=user_row(id=1)):
            with self.app.test_request_context(method='POST', data={'username': 'alice'}):
                session['user_id'] = 1
                self.controller.share_note(5)
        self.note_model.share_note.assert_not_called()


class TestDeleteNote(NoteControllerTestBase):
    def test_not_owned_flashes_and_skips_delete(self):
        self.note_model.get_note_by_id.return_value = note_row(user_id=999)
        with self.app.test_request_context(method='POST'):
            session['user_id'] = 1
            response = self.controller.delete_note(5)
        self.assertEqual(response.status_code, 302)
        self.note_model.delete_note.assert_not_called()

    @patch('app.controllers.note_controller.os.remove')
    @patch('app.controllers.note_controller.Flashcard')
    def test_owned_deletes_flashcards_and_note(self, mock_flashcard, mock_remove):
        self.note_model.get_note_by_id.return_value = note_row(user_id=1, pdf_url='uploads/notes/x.pdf')
        with self.app.test_request_context(method='POST'):
            session['user_id'] = 1
            self.controller.delete_note(5)
        mock_flashcard.return_value.delete_flashcards_for_note.assert_called_once_with(5)
        self.note_model.delete_note.assert_called_once_with(5)


class TestSummarizeNote(NoteControllerTestBase):
    def test_requires_login_401(self):
        with self.app.test_request_context(method='POST'):
            resp, status = self.controller.summarize_note(5)
        self.assertEqual(status, 401)

    def test_note_not_found_404(self):
        self.note_model.get_note_by_id.return_value = None
        with self.app.test_request_context(method='POST'):
            session['user_id'] = 1
            resp, status = self.controller.summarize_note(5)
        self.assertEqual(status, 404)

    @patch('app.controllers.note_controller.generate_summary_from_pdf', return_value='A summary')
    @patch('app.controllers.note_controller.os.path.exists', return_value=True)
    def test_success_returns_summary(self, mock_exists, mock_summary):
        self.note_model.get_note_by_id.return_value = note_row(user_id=1)
        with self.app.test_request_context(method='POST'):
            session['user_id'] = 1
            resp, status = self.controller.summarize_note(5)
        self.assertEqual(status, 200)
        self.assertEqual(resp.get_json()['summary'], 'A summary')


class TestChatNote(NoteControllerTestBase):
    @patch('app.controllers.note_controller.chat_with_note', return_value='the reply')
    @patch('app.controllers.note_controller.os.path.exists', return_value=True)
    def test_chat_success(self, mock_exists, mock_chat):
        self.note_model.get_note_by_id.return_value = note_row(user_id=1, content_text='cached text')
        with self.app.test_request_context(method='POST', json={'message': 'What is it?', 'history': []}):
            session['user_id'] = 1
            resp, status = self.controller.chat_note(5)
        self.assertEqual(status, 200)
        self.assertEqual(resp.get_json()['reply'], 'the reply')

    @patch('app.controllers.note_controller.os.path.exists', return_value=True)
    def test_empty_message_400(self, mock_exists):
        self.note_model.get_note_by_id.return_value = note_row(user_id=1)
        with self.app.test_request_context(method='POST', json={'message': '   '}):
            session['user_id'] = 1
            resp, status = self.controller.chat_note(5)
        self.assertEqual(status, 400)


if __name__ == '__main__':
    unittest.main()
