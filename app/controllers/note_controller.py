import os
import uuid
from flask import request, current_app, url_for, flash,  jsonify
from werkzeug.utils import secure_filename
from app.controllers.base_controller import BaseController
from app.models.note import Note
from app.models.database import get_user_by_username


class NoteController(BaseController):
    ALLOWED_EXTENSIONS = {'.pdf'}

    def __init__(self):
        self.note_model = Note()
        self.note_model.create_notes_table()
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
