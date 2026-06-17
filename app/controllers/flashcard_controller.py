from flask import request, flash
from app.controllers.base_controller import BaseController
from app.models.flashcard import Flashcard
from app.models.note import Note


class FlashcardController(BaseController):
    def __init__(self):
        self.flashcard_model = Flashcard()
        self.note_model = Note()
        self.flashcard_model.create_flashcards_table()

    def add_flashcard(self, note_id):
        user_id = self.get_current_user_id()
        if not user_id:
            return self.redirect('auth.login')

        note = self.note_model.get_note_by_id(note_id)
        if not note or note['user_id'] != user_id:
            flash('Unable to add flashcard. Note not found.', 'error')
            return self.redirect('home.notes')

        front_text = (request.form.get('front_text') or '').strip()
        back_text = (request.form.get('back_text') or '').strip()

        if not front_text or not back_text:
            flash('Both sides of the flashcard are required.', 'error')
            return self.redirect('home.notes')

        self.flashcard_model.create_flashcard(note_id, user_id, front_text, back_text)
        flash('Flashcard added successfully.', 'success')
        return self.redirect('home.notes')

    def list_flashcards(self, note_id):
        user_id = self.get_current_user_id()
        if not user_id:
            return self.redirect('auth.login')

        note = self.note_model.get_note_by_id(note_id)
        if not note or note['user_id'] != user_id:
            flash('Note not found.', 'error')
            return self.redirect('home.notes')

        flashcards = self.flashcard_model.get_flashcards_for_note(note_id, user_id)
        return self.render('flashcards.html', note=note, flashcards=flashcards)

    def delete_flashcard(self, flashcard_id):
        user_id = self.get_current_user_id()
        if not user_id:
            return self.redirect('auth.login')

        self.flashcard_model.delete_flashcard(flashcard_id, user_id)
        flash('Flashcard deleted.', 'success')
        return self.redirect('home.notes')
