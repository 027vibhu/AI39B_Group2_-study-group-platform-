import os
import json
import uuid
from flask import request, current_app, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from app.controllers.base_controller import BaseController
from app.models.note import Note
from app.models.flashcard import Flashcard
from app.models.database import get_user_by_username
from app.services.summary_ai import generate_summary_from_pdf
from app.services.flashcard_ai import extract_pdf_text
from app.services.pdf_chat import chat_with_note, render_pdf_images


class NoteController(BaseController):
    ALLOWED_EXTENSIONS = {'.pdf'}

    def __init__(self):
        self.note_model = Note()
        self.note_model.create_notes_table()
        self.note_model.ensure_content_column()
        self.note_model.create_note_shares_table()

    def _is_allowed_file(self, filename):
        _, ext = os.path.splitext(filename.lower())
        return ext in self.ALLOWED_EXTENSIONS

    def upload_note(self):
        user_id = self.get_current_user_id()
        if not user_id:
            return self.redirect('auth.login')

        file = request.files.get('pdf')
        title = (request.form.get('title') or '').strip()
        description = (request.form.get('description') or '').strip()

        if not file or not file.filename:
            return self.redirect('home.notes')

        filename = secure_filename(file.filename)
        if not self._is_allowed_file(filename):
            return self.redirect('home.notes')

        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'notes')
        os.makedirs(upload_dir, exist_ok=True)

        stored_name = f"{uuid.uuid4().hex}{os.path.splitext(filename)[1].lower()}"
        file_path = os.path.join(upload_dir, stored_name)
        file.save(file_path)

        pdf_url = f"uploads/notes/{stored_name}"
        note_title = title or filename

        self.note_model.create_note(user_id, note_title, pdf_url, description or None)
        return self.redirect('home.notes')

    def share_note(self, note_id):
        user_id = self.get_current_user_id()
        if not user_id:
            return self.redirect('auth.login')

        note = self.note_model.get_note_by_id(note_id)
        if not note or note['user_id'] != user_id:
            flash('Note not found.', 'error')
            return self.redirect('home.notes')

        username = (request.form.get('username') or '').strip()
        if not username:
            flash('Please enter a username to share with.', 'error')
            return self.redirect('home.notes')

        recipient = get_user_by_username(username)
        if not recipient:
            flash(f'No user found with username "{username}".', 'error')
            return self.redirect('home.notes')

        if recipient['id'] == user_id:
            flash('You cannot share a note with yourself.', 'error')
            return self.redirect('home.notes')

        self.note_model.share_note(note_id, recipient['id'], user_id)
        flash(f'Note shared with {recipient["username"]}.', 'success')
        return self.redirect('home.notes')

    def delete_note(self, note_id):
        user_id = self.get_current_user_id()
        if not user_id:
            return self.redirect('auth.login')

        note = self.note_model.get_note_by_id(note_id)
        if not note or note['user_id'] != user_id:
            flash('Note not found.', 'error')
            return self.redirect('home.notes')

        Flashcard().delete_flashcards_for_note(note_id)
        self.note_model.delete_note(note_id)

        if note.get('pdf_url'):
            file_path = os.path.join(current_app.root_path, 'static', note['pdf_url'])
            try:
                os.remove(file_path)
            except OSError:
                pass

        flash('Note deleted.', 'success')
        return self.redirect('home.notes')

    def list_notes(self):
        user_id = self.get_current_user_id()
        if not user_id:
            return self.redirect('auth.login')

        notes = self.note_model.get_notes_for_user(user_id)
        shared_notes = self.note_model.get_shared_notes_for_user(user_id)
        return self.render('notes.html', notes=notes, shared_notes=shared_notes)

    def _accessible_note(self, note_id, user_id):
        """Return the note if the user owns it or it was shared with them."""
        note = self.note_model.get_note_by_id(note_id)
        if not note:
            return None
        if note['user_id'] == user_id:
            return note
        shared_ids = {n['id'] for n in self.note_model.get_shared_notes_for_user(user_id)}
        return note if note_id in shared_ids else None

    def view_note(self, note_id):
        user_id = self.get_current_user_id()
        if not user_id:
            return self.redirect('auth.login')

        note = self._accessible_note(note_id, user_id)
        if not note:
            flash('Note not found.', 'error')
            return self.redirect('home.notes')

        return self.render('note_view.html', note=note)

    def summarize_note(self, note_id):
        user_id = self.get_current_user_id()
        if not user_id:
            return jsonify({'error': 'Authentication required.'}), 401

        note = self._accessible_note(note_id, user_id)
        if not note:
            return jsonify({'error': 'Note not found.'}), 404

        pdf_path = os.path.join(current_app.root_path, 'static', note['pdf_url'])
        if not os.path.exists(pdf_path):
            return jsonify({'error': 'The PDF for this note could not be found.'}), 404

        try:
            summary = generate_summary_from_pdf(pdf_path)
        except (ValueError, RuntimeError) as exc:
            return jsonify({'error': str(exc)}), 400
        except Exception as exc:
            current_app.logger.exception('Summary generation failed for note %s', note_id)
            return jsonify({'error': f'Summary generation failed: {type(exc).__name__}: {exc}'}), 500

        return jsonify({'summary': summary}), 200

    def _get_cached_text(self, note, pdf_path):
        """Return the note's extracted text, parsing and caching it on first use."""
        text = (note.get('content_text') or '').strip()
        if text:
            return text
        text = (extract_pdf_text(pdf_path) or '').strip()
        if text:
            self.note_model.set_content_text(note['id'], text)
        return text

    def _get_cached_images(self, note, pdf_path):
        """Return rendered page images for a scanned PDF, rendering once and caching."""
        cached = note.get('content_images')
        if cached:
            try:
                images = json.loads(cached)
                if images:
                    return images
            except (ValueError, TypeError):
                pass  # corrupt cache — re-render below
        images = render_pdf_images(pdf_path)
        if images:
            self.note_model.set_content_images(note['id'], json.dumps(images))
        return images

    def chat_note(self, note_id):
        user_id = self.get_current_user_id()
        if not user_id:
            return jsonify({'error': 'Authentication required.'}), 401

        note = self._accessible_note(note_id, user_id)
        if not note:
            return jsonify({'error': 'Note not found.'}), 404

        payload = request.get_json(silent=True) or {}
        message = (payload.get('message') or '').strip()
        history = payload.get('history') or []
        if not message:
            return jsonify({'error': 'Please enter a question.'}), 400

        pdf_path = os.path.join(current_app.root_path, 'static', note['pdf_url'])
        if not os.path.exists(pdf_path):
            return jsonify({'error': 'The PDF for this note could not be found.'}), 404

        try:
            content_text = self._get_cached_text(note, pdf_path)
            # Scanned PDFs with no embedded text fall back to cached rendered images.
            images = None if content_text else self._get_cached_images(note, pdf_path)
            reply = chat_with_note(content_text, message, history=history, images_b64=images)
        except (ValueError, RuntimeError) as exc:
            return jsonify({'error': str(exc)}), 400
        except Exception as exc:
            current_app.logger.exception('Chat failed for note %s', note_id)
            return jsonify({'error': f'Chat failed: {type(exc).__name__}: {exc}'}), 500

        return jsonify({'reply': reply}), 200
