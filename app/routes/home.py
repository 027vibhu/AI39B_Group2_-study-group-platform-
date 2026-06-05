from flask import Blueprint, render_template, redirect, url_for, session, request, current_app, flash, jsonify, send_from_directory
from app.models.room import (
    create_room as create_room_record,
    create_user_room,
    delete_room_by_code,
    get_joined_rooms_for_user,
    get_room_by_code,
    get_room_by_id,
    is_user_banned_from_room,
    is_user_in_room,
)
from app.models.message import get_messages_for_room
from app.models.presence_model import get_online_users, get_offline_users
from app.models.message_vote import get_vote_count, get_user_vote
from app.controllers import MessageVoteController
from app.models.database import get_user_by_id, get_user_by_username, update_user_avatar, update_user_profile
from app.models.shared_file import create_shared_file, get_shared_file_by_id, get_shared_files_for_room
import random
import os
import uuid
from werkzeug.utils import secure_filename
from app.controllers.moderation_controller import ModerationController
from app.controllers.browse_rooms_controller import BrowseRoomsController

ALLOWED_SHARED_FILE_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.webp',
    '.pdf', '.doc', '.docx', '.ppt', '.pptx',
    '.xls', '.xlsx', '.csv', '.txt', '.md',
    '.zip', '.rar', '.7z'
}
MAX_SHARED_FILE_SIZE = 25 * 1024 * 1024  # 25MB

class HomeRoutes:
    def __init__(self):
        self.bp = Blueprint('home', __name__)

    def register(self):
        # before_request
        self.bp.before_app_request(self.require_login_for_protected_pages)

        # routes
        self.bp.route('/')(self.index)
        self.bp.route('/join_room')(self.join_room)
        self.bp.route('/browse_rooms')(self.browse_rooms)
        self.bp.route('/create')(self.create)
        self.bp.route('/chat/<room_code>')(self.chat)
        self.bp.route('/chat/<room_code>/shared-files', methods=['GET'])(self.list_shared_files)
        self.bp.route('/chat/<room_code>/shared-files', methods=['POST'])(self.upload_shared_file)
        self.bp.route('/files/<int:file_id>/download')(self.download_shared_file)
        self.bp.route('/files/<int:file_id>/view')(self.view_shared_file)
        self.bp.route('/message/<int:message_id>/vote', methods=['POST'])(self.vote_message)
        self.bp.route('/chat/<room_code>/delete', methods=['POST'])(self.delete_chat)
        self.bp.context_processor(self.inject_joined_rooms)
        self.bp.route('/profile')(self.profile)
        self.bp.route('/moderation')(self.moderation)
        self.bp.route('/moderation/action', methods=['POST'])(self.moderation_action)
        self.bp.route('/profile/update', methods=['POST'])(self.update_profile)
        self.bp.route('/profile/avatar', methods=['POST'])(self.update_avatar)
        self.bp.route('/create_room', methods=['GET', 'POST'])(self.create_room)

        return self.bp

    def require_login_for_protected_pages(self):
        if request.endpoint is None:
            return None

        if request.endpoint.startswith('static'):
            return None

        allowed_endpoints = {
            'home.index',
            'auth.login',
            'auth.login_post',
            'auth.register',
            'auth.reset_password',
            'auth.logout',
        }

        if request.endpoint in allowed_endpoints:
            return None

        if not session.get('user_id'):
            return redirect(url_for('auth.login'))

        return None

    def index(self):
        return render_template('index.html')

    def join_room(self):
        return render_template('join_room.html')

    def browse_rooms(self):
        controller = BrowseRoomsController()
        return controller.show_browse_rooms()

    def _remember_joined_room(self, room_code):
        joined_room_codes = session.get('joined_room_codes', [])
        if room_code not in joined_room_codes:
            joined_room_codes.insert(0, room_code)
            session['joined_room_codes'] = joined_room_codes[:8]
            session.modified = True

    def _remember_joined_room_for_user(self, user_id, room_id):
        create_user_room(user_id, room_id)

    def create(self):
        return redirect(url_for('home.create_room'))

    def _generate_unique_room_code(self):
        while True:
            code = str(random.randint(100000, 999999))
            if not get_room_by_code(code):
                return code

    def chat(self, room_code):
        room = get_room_by_code(room_code)
        if not room:
            return "Room not found", 404

        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('auth.login'))

        current_user = get_user_by_id(user_id)
        if not current_user:
            session.clear()
            return redirect(url_for('auth.login'))

        username = current_user['username']

        if is_user_banned_from_room(username, room['code'], room.get('name')):
            return "You are banned from this room.", 403

        if room['is_private']:
            if not user_id:
                return "Private room. Login required.", 403
            if not is_user_in_room(user_id, room['id']):
                create_user_room(user_id, room['id'])
                self._remember_joined_room_for_user(user_id, room['id'])
        elif user_id:
            self._remember_joined_room_for_user(user_id, room['id'])
        else:
            self._remember_joined_room(room_code)

        messages = get_messages_for_room(room['id'])
        for msg in messages:
            vote_counts = get_vote_count(msg['id'])
            msg['upvotes'] = vote_counts.get('upvotes', 0)
            msg['downvotes'] = vote_counts.get('downvotes', 0)
            msg['user_vote'] = get_user_vote(msg['id'], user_id) if user_id else None
        online_members = get_online_users(room['id'])
        offline_members = get_offline_users(room['id'])

        return render_template(
            'chat.html',
            room=room,
            room_code=room_code,
            messages=messages,
            online_members=online_members,
            offline_members=offline_members,
        )

    def _get_shared_file_upload_dir(self):
        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'shared_files')
        os.makedirs(upload_dir, exist_ok=True)
        return upload_dir

    def _authorize_room_access(self, room, user_id):
        if not room:
            return False
        if room['is_private'] and not is_user_in_room(user_id, room['id']):
            return False
        return True

    def list_shared_files(self, room_code):
        room = get_room_by_code(room_code)
        if not room:
            return jsonify({'error': 'Room not found'}), 404

        user_id = session.get('user_id')
        if not self._authorize_room_access(room, user_id):
            return jsonify({'error': 'Access denied'}), 403

        shared_files = get_shared_files_for_room(room['id'])
        files = [
            {
                'id': item['id'],
                'original_filename': item['original_filename'],
                'uploader_username': item['uploader_username'],
                'mime_type': item['mime_type'],
                'file_size': item['file_size'],
                'uploaded_at': item['uploaded_at'].strftime('%Y-%m-%d %H:%M:%S') if hasattr(item['uploaded_at'], 'strftime') else item['uploaded_at'],
                'download_url': url_for('home.download_shared_file', file_id=item['id']),
                'view_url': url_for('home.view_shared_file', file_id=item['id']),
            }
            for item in shared_files
        ]
        return jsonify({'status': 'success', 'files': files}), 200

    def upload_shared_file(self, room_code):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('auth.login'))

        room = get_room_by_code(room_code)
        if not room:
            return "Room not found", 404

        if room['is_private'] and not is_user_in_room(user_id, room['id']):
            return "Access denied", 403

        current_user = get_user_by_id(user_id)
        if not current_user:
            session.clear()
            return redirect(url_for('auth.login'))

        file = request.files.get('shared_file')
        if not file or not file.filename:
            flash('Please select a file to share.', 'warning')
            return redirect(url_for('home.chat', room_code=room_code))

        original_filename = secure_filename(file.filename)
        if not original_filename:
            flash('Invalid file name.', 'warning')
            return redirect(url_for('home.chat', room_code=room_code))

        _, ext = os.path.splitext(original_filename)
        ext = ext.lower()
        if ext not in ALLOWED_SHARED_FILE_EXTENSIONS:
            flash('Unsupported file type. Please upload a document, image, or compressed archive.', 'warning')
            return redirect(url_for('home.chat', room_code=room_code))

        stored_filename = f"{uuid.uuid4().hex}{ext}"
        upload_dir = self._get_shared_file_upload_dir()
        saved_path = os.path.join(upload_dir, stored_filename)
        file.save(saved_path)

        file_size = os.path.getsize(saved_path)
        if file_size > MAX_SHARED_FILE_SIZE:
            os.remove(saved_path)
            flash('File is too large. Maximum allowed size is 25 MB.', 'warning')
            return redirect(url_for('home.chat', room_code=room_code))

        mime_type = file.mimetype or 'application/octet-stream'

        create_shared_file(room['id'], current_user['username'], original_filename, stored_filename, mime_type, file_size)

        flash('File shared successfully.', 'success')
        return redirect(url_for('home.chat', room_code=room_code))

    def _load_shared_file_for_user(self, file_id, user_id):
        file_record = get_shared_file_by_id(file_id)
        if not file_record:
            return None, None
        room = get_room_by_id(file_record['room_id'])
        if not self._authorize_room_access(room, user_id):
            return None, room
        return file_record, room

    def download_shared_file(self, file_id):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('auth.login'))

        file_record, _ = self._load_shared_file_for_user(file_id, user_id)
        if not file_record:
            return "File not found or access denied", 404

        upload_dir = self._get_shared_file_upload_dir()
        return send_from_directory(
            upload_dir,
            file_record['stored_filename'],
            as_attachment=True,
            attachment_filename=file_record['original_filename'],
        )

    def view_shared_file(self, file_id):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('auth.login'))

        file_record, _ = self._load_shared_file_for_user(file_id, user_id)
        if not file_record:
            return "File not found or access denied", 404

        upload_dir = self._get_shared_file_upload_dir()
        return send_from_directory(
            upload_dir,
            file_record['stored_filename'],
            as_attachment=False,
            mimetype=file_record['mime_type'],
        )

    def vote_message(self, message_id):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401

        vote_type = request.form.get('vote_type') or (request.get_json(silent=True) or {}).get('vote_type')
        if vote_type not in ('upvote', 'downvote'):
            return jsonify({'error': 'Invalid vote type'}), 400

        controller = MessageVoteController()
        result = controller.handle(message_id, user_id, vote_type)
        return jsonify(result)

    def delete_chat(self, room_code):
        delete_room_by_code(room_code)
        return redirect(url_for('home.profile'))

    def inject_joined_rooms(self):
        user_id = session.get('user_id')
        joined_rooms = get_joined_rooms_for_user(user_id) if user_id else []

        current_room_code = None
        if request.endpoint == 'home.chat':
            current_room_code = request.view_args.get('room_code') if request.view_args else None

        current_user = None
        if user_id:
            current_user = get_user_by_id(user_id)

        return {
            'joined_rooms': joined_rooms,
            'current_room_code': current_room_code,
            'current_user': current_user,
        }

    def profile(self):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('auth.login'))

        user = get_user_by_id(user_id)
        if not user:
            session.clear()
            return redirect(url_for('auth.login'))

        return render_template('profile.html', user=user)

    def moderation(self):
        controller = ModerationController()
        return controller.show_moderation()

    def moderation_action(self):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'status': 'error', 'message': 'Authentication required.'}), 401

        current_user = get_user_by_id(user_id)
        if not current_user:
            return jsonify({'status': 'error', 'message': 'Invalid session.'}), 401

        # moderation allowed for admins/moderators or room owners (checked later)

        payload = request.get_json(silent=True) or request.form
        room_code = (payload.get('room_code') or '').strip().upper()
        target_username = (payload.get('username') or '').strip()
        action = (payload.get('action') or '').strip().lower()
        reason = (payload.get('reason') or '').strip() or None
        duration_minutes = payload.get('duration_minutes')

        if action not in {'kick', 'ban'}:
            return jsonify({'status': 'error', 'message': 'Action must be kick or ban.'}), 400

        if not room_code or not target_username:
            return jsonify({'status': 'error', 'message': 'Room code and username are required.'}), 400

        room = get_room_by_code(room_code)
        if not room:
            return jsonify({'status': 'error', 'message': 'Room not found.'}), 404

        # Check permissions: admin/moderator or owner of the room
        role = session.get('role')
        if role not in ('admin', 'moderator') and room.get('owner_id') != current_user['id']:
            if request.is_json:
                return jsonify({'status': 'error', 'message': 'Moderator privileges required.'}), 403
            flash('Moderator privileges required.', 'danger')
            return redirect(url_for('home.moderation'))

        target_user = get_user_by_username(target_username)
        if not target_user:
            return jsonify({'status': 'error', 'message': 'Target user not found.'}), 404

        if action == 'ban':
            try:
                duration_minutes = int(duration_minutes) if duration_minutes not in (None, '') else None
            except (TypeError, ValueError):
                return jsonify({'status': 'error', 'message': 'Ban duration must be a number of minutes.'}), 400

        log_room_action(target_username, room['code'], room.get('name') or room['code'], action, duration_minutes, reason)
        log_moderation_action(
            room['id'],
            room['code'],
            current_user['id'],
            current_user['username'],
            target_username,
            action,
            duration_minutes,
            reason,
        )

        socketio.emit(
            'moderation_action',
            {
                'action': action,
                'room_code': room['code'],
                'username': target_username,
                'message': reason or f'You were {action}ed from this room.',
            },
            room=room['code'],
        )

        message = f"{target_username} was {action}ed in room {room['code']}."
        if action == 'ban' and duration_minutes:
            message = f"{target_username} was banned for {duration_minutes} minutes in room {room['code']}."

        if request.accept_mimetypes.best == 'application/json' or request.is_json:
            return jsonify({'status': 'success', 'message': message})

        flash(message, 'success')
        return redirect(url_for('home.moderation'))

    def update_profile(self):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('auth.login'))

        first_name = (request.form.get('first_name') or '').strip()
        last_name = (request.form.get('last_name') or '').strip()
        school = (request.form.get('school') or '').strip()
        address = (request.form.get('address') or '').strip()
        bio = (request.form.get('bio') or '').strip()

        update_user_profile(user_id, first_name, last_name, school, address, bio)
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('home.profile'))

    def update_avatar(self):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('auth.login'))

        file = request.files.get('avatar')
        if not file or not file.filename:
            return redirect(url_for('home.profile'))

        filename = secure_filename(file.filename)
        _, ext = os.path.splitext(filename.lower())
        allowed_ext = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
        if ext not in allowed_ext:
            return redirect(url_for('home.profile'))

        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'avatars')
        os.makedirs(upload_dir, exist_ok=True)
        stored_name = f"{uuid.uuid4().hex}{ext}"
        file.save(os.path.join(upload_dir, stored_name))

        avatar_url = f"uploads/avatars/{stored_name}"
        update_user_avatar(user_id, avatar_url)

        return redirect(url_for('home.profile'))

    def create_room(self):
        if request.method == 'POST':
            room_name = request.form.get('room_name', '').strip()
            subject_tags = (request.form.get('selected_tags') or '').strip()
            submitted_code = (request.form.get('room_code') or '').strip().upper()
            if len(submitted_code) == 6 and submitted_code.isalnum() and not get_room_by_code(submitted_code):
                code = submitted_code
            else:
                code = self._generate_unique_room_code()

            is_private = request.form.get('is_private') == '1'

            user_id = session.get('user_id')
            new_room = create_room_record(code, room_name or f'Room {code}', is_private, subject_tags, owner_id=user_id)

            user_id = session.get('user_id')
            if user_id:
                self._remember_joined_room_for_user(user_id, new_room['id'])
            else:
                self._remember_joined_room(code)

            return redirect(url_for('home.chat', room_code=code))

        return render_template('createroom.html', room_code=self._generate_unique_room_code())


# Expose blueprint
bp = HomeRoutes().register()
