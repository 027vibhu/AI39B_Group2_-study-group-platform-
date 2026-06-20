"""Unit tests for FlashcardController (Note + Flashcard classes + AI service)."""

import unittest
from unittest.mock import patch

from flask import session

from tests.support import make_controller_app
from tests.support.fixtures import note_row


class FlashcardControllerTestBase(unittest.TestCase):
    def setUp(self):
        self.app = make_controller_app()
        self.note_patcher = patch('app.controllers.flashcard_controller.Note')
        self.flash_patcher = patch('app.controllers.flashcard_controller.Flashcard')
        self.Note = self.note_patcher.start()
        self.Flashcard = self.flash_patcher.start()
        self.addCleanup(self.note_patcher.stop)
        self.addCleanup(self.flash_patcher.stop)
        self.note_model = self.Note.return_value
        self.flash_model = self.Flashcard.return_value
        from app.controllers.flashcard_controller import FlashcardController
        self.controller = FlashcardController()


class TestGenerateFlashcards(FlashcardControllerTestBase):
    def test_requires_login(self):
        with self.app.test_request_context(method='POST'):
            response = self.controller.generate_flashcards(5)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login', response.location)

    def test_unowned_note_redirects_to_notes(self):
        self.note_model.get_note_by_id.return_value = note_row(user_id=999)
        with self.app.test_request_context(method='POST'):
            session['user_id'] = 1
            response = self.controller.generate_flashcards(5)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/home/notes', response.location)

    @patch('app.controllers.flashcard_controller.generate_cards_from_pdf')
    @patch('app.controllers.flashcard_controller.os.path.exists', return_value=True)
    def test_success_creates_set_and_cards(self, mock_exists, mock_generate):
        self.note_model.get_note_by_id.return_value = note_row(user_id=1)
        mock_generate.return_value = [('Q1', 'A1'), ('Q2', 'A2')]
        self.flash_model.create_set.return_value = 99
        with self.app.test_request_context(method='POST'):
            session['user_id'] = 1
            response = self.controller.generate_flashcards(5)
        self.flash_model.create_set.assert_called_once()
        self.assertEqual(self.flash_model.create_flashcard.call_count, 2)
        self.assertEqual(response.status_code, 302)


class TestStudyFlashcards(FlashcardControllerTestBase):
    @patch('app.controllers.flashcard_controller.BaseController.render', return_value='sets_page')
    def test_no_set_id_shows_set_list(self, mock_render):
        self.note_model.get_note_by_id.return_value = note_row(user_id=1)
        self.flash_model.get_sets_for_note.return_value = [{'id': 1}]
        with self.app.test_request_context(method='GET'):
            session['user_id'] = 1
            result = self.controller.study_flashcards(5)
        self.assertEqual(result, 'sets_page')
        self.assertEqual(mock_render.call_args.args[0], 'flashcard_sets.html')

    @patch('app.controllers.flashcard_controller.BaseController.render', return_value='cards_page')
    def test_with_set_id_shows_cards(self, mock_render):
        self.note_model.get_note_by_id.return_value = note_row(id=5, user_id=1)
        self.flash_model.get_set_by_id.return_value = {'id': 99, 'note_id': 5}
        self.flash_model.get_flashcards_for_set.return_value = [{'id': 1}]
        with self.app.test_request_context(method='GET', query_string={'set_id': '99'}):
            session['user_id'] = 1
            result = self.controller.study_flashcards(5)
        self.assertEqual(result, 'cards_page')
        self.assertEqual(mock_render.call_args.args[0], 'flashcards.html')


if __name__ == '__main__':
    unittest.main()
