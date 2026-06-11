import os
from flask import render_template, request, session, redirect, url_for, flash, current_app
from app.controllers.base_controller import BaseController
from app.models.room import get_all_rooms, delete_room_by_id, get_room_by_id
from app.models.note import Note
from app.models.message import get_messages_for_room, get_message_by_id, delete_message
from app.models.database import get_all_users, delete_user, get_user_by_id


class AdminController(BaseController):
    def __init__(self):
        self.note_model = Note()

    def dashboard(self):
        rooms = get_all_rooms() or []
        notes = self.note_model.get_all_notes() or []
        users = get_all_users() or []

        # Build a per-room message list so admins can delete individual messages.
        rooms_with_messages = []
        for room in rooms:
            messages = get_messages_for_room(room['id']) or []
            rooms_with_messages.append({'room': room, 'messages': messages})

        return render_template(
            'admin.html',
            rooms=rooms,
            notes=notes,
            users=users,
            rooms_with_messages=rooms_with_messages,
        )

    def delete_room(self, room_id):
        room = get_room_by_id(room_id)
        if not room:
            flash('Room not found.', 'danger')
            return redirect(url_for('admin.dashboard'))
        delete_room_by_id(room_id)
        flash(f"Room {room.get('code')} deleted.", 'success')
        return redirect(url_for('admin.dashboard'))

    def delete_note(self, note_id):
        note = self.note_model.get_note_by_id(note_id)
        if not note:
            flash('Note not found.', 'danger')
            return redirect(url_for('admin.dashboard'))

        self.note_model.delete_note(note_id)

        # Best-effort removal of the stored file.
        if note.get('pdf_url'):
            file_path = os.path.join(current_app.root_path, 'static', note['pdf_url'])
            try:
                os.remove(file_path)
            except OSError:
                pass

        flash('Note deleted.', 'success')
        return redirect(url_for('admin.dashboard'))

    def delete_user(self, user_id):
        if user_id == session.get('user_id'):
            flash('You cannot delete your own admin account while signed in.', 'warning')
            return redirect(url_for('admin.dashboard'))

        target = get_user_by_id(user_id)
        if not target:
            flash('User not found.', 'danger')
            return redirect(url_for('admin.dashboard'))

        delete_user(user_id)
        flash(f"User {target.get('username')} deleted.", 'success')
        return redirect(url_for('admin.dashboard'))

    def delete_message(self, message_id):
        message = get_message_by_id(message_id)
        if not message:
            flash('Message not found.', 'danger')
            return redirect(url_for('admin.dashboard'))
        delete_message(message_id)
        flash('Message deleted.', 'success')
        return redirect(url_for('admin.dashboard'))
