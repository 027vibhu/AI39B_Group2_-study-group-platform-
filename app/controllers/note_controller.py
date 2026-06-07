import os
import uuid
from flask import request, current_app, url_for
from werkzeug.utils import secure_filename
from app.controllers.base_controller import BaseController
from app.models.note import Note


class NoteController(BaseController):
    ALLOWED_EXTENSIONS = {'.pdf'}

    def __init__(self):
        self.note_model = Note()
        self.note_model.create_notes_table()

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
            return self.redirect('home.profile')

        filename = secure_filename(file.filename)
        if not self._is_allowed_file(filename):
            return self.redirect('home.profile')

        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'notes')
        os.makedirs(upload_dir, exist_ok=True)

        stored_name = f"{uuid.uuid4().hex}{os.path.splitext(filename)[1].lower()}"
        file_path = os.path.join(upload_dir, stored_name)
        file.save(file_path)

        pdf_url = f"uploads/notes/{stored_name}"
        note_title = title or filename

        self.note_model.create_note(user_id, note_title, pdf_url, description or None)
        return self.redirect('home.profile')

    def list_notes(self):
        user_id = self.get_current_user_id()
        if not user_id:
            return self.redirect('auth.login')

        notes = self.note_model.get_notes_for_user(user_id)
        return self.render('notes.html', notes=notes)
