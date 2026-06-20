import os
from datetime import datetime

from flask import flash, current_app, request
from app.controllers.base_controller import BaseController
from app.models.note import Note
from app.models.flashcard import Flashcard
from app.services.flashcard_ai import generate_cards_from_pdf


class FlashcardController(BaseController):
    def __init__(self):
        self.note_model = Note()
        self.flashcard_model = Flashcard()
        self.flashcard_model.create_flashcards_table()

    def _owned_note(self, note_id, user_id):
        note = self.note_model.get_note_by_id(note_id)
        if not note or note['user_id'] != user_id:
            return None
        return note

    def generate_flashcards(self, note_id):
        user_id = self.get_current_user_id()
        if not user_id:
            return self.redirect('auth.login')

        note = self._owned_note(note_id, user_id)
        if not note:
            flash('Note not found.', 'error')
            return self.redirect('home.notes')

        pdf_path = os.path.join(current_app.root_path, 'static', note['pdf_url'])
        if not os.path.exists(pdf_path):
            flash('The PDF for this note could not be found.', 'error')
            return self.redirect('home.notes')

        try:
            cards = generate_cards_from_pdf(pdf_path)
        except (ValueError, RuntimeError) as exc:
            flash(str(exc), 'error')
            return self.redirect('home.study_flashcards', note_id=note_id)
        except Exception as exc:
            current_app.logger.exception('Flashcard generation failed for note %s', note_id)
            flash(f'Flashcard generation failed: {type(exc).__name__}: {exc}', 'error')
            return self.redirect('home.study_flashcards', note_id=note_id)

        title = f"{len(cards)} cards · {datetime.now().strftime('%b %d, %Y %I:%M %p')}"
        set_id = self.flashcard_model.create_set(note_id, user_id, title, len(cards))
        for question, answer in cards:
            self.flashcard_model.create_flashcard(note_id, user_id, question, answer, set_id=set_id)

        flash(f'Generated {len(cards)} flashcards for "{note["title"]}".', 'success')
        return self.redirect('home.study_flashcards', note_id=note_id, set_id=set_id)

    def study_flashcards(self, note_id):
        user_id = self.get_current_user_id()
        if not user_id:
            return self.redirect('auth.login')

        note = self._owned_note(note_id, user_id)
        if not note:
            flash('Note not found.', 'error')
            return self.redirect('home.notes')

        set_id = request.args.get('set_id', type=int)
        if set_id:
            card_set = self.flashcard_model.get_set_by_id(set_id)
            if not card_set or card_set['note_id'] != note_id:
                flash('Flashcard set not found.', 'error')
                return self.redirect('home.study_flashcards', note_id=note_id)
            flashcards = self.flashcard_model.get_flashcards_for_set(set_id)
            return self.render('flashcards.html', note=note, flashcards=flashcards, card_set=card_set)

        sets = self.flashcard_model.get_sets_for_note(note_id)
        return self.render('flashcard_sets.html', note=note, sets=sets)
