from flask import Blueprint, render_template, redirect, url_for, session, request, current_app, flash
from app.models import (
    create_room as create_room_record,
    create_user_room,
    delete_room_by_code,
    get_joined_rooms_for_user,
    get_messages_for_room,
    get_room_by_code,
    get_online_users,
    get_offline_users,
)
from app.models.database import get_user_by_id, update_user_avatar, update_user_profile
import random
import os
import uuid
from werkzeug.utils import secure_filename
from app.controllers.moderation_controller import ModerationController
from app.controllers.browse_rooms_controller import BrowseRoomsController

bp = Blueprint('home', __name__)


@bp.before_app_request
def require_login_for_protected_pages():
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


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/join_room')
def join_room():
    return render_template('join_room.html')


@bp.route('/browse_rooms')
def browse_rooms():
    """
    Route handler for browsing all public rooms.
    Instantiates BrowseRoomsController and calls show_browse_rooms().
    """
    controller = BrowseRoomsController()
    return controller.show_browse_rooms()


def _remember_joined_room(room_code):
    joined_room_codes = session.get('joined_room_codes', [])
    if room_code not in joined_room_codes:
        joined_room_codes.insert(0, room_code)
        session['joined_room_codes'] = joined_room_codes[:8]
        session.modified = True


def _remember_joined_room_for_user(user_id, room_id):
    create_user_room(user_id, room_id)


@bp.route('/create')
def create():
    return redirect(url_for('home.create_room'))


def _generate_unique_room_code():
    while True:
        code = str(random.randint(100000, 999999))
        if not get_room_by_code(code):
            return code


@bp.route('/chat/<room_code>')
def chat(room_code):
    room = get_room_by_code(room_code)
    if not room:
        return "Room not found", 404

    user_id = session.get('user_id')
    if user_id:
        _remember_joined_room_for_user(user_id, room['id'])
    else:
        _remember_joined_room(room_code)
    
    # Fetch previous messages and member presence
    messages = get_messages_for_room(room['id'])
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


@bp.route('/chat/<room_code>/delete', methods=['POST'])
def delete_chat(room_code):
    delete_room_by_code(room_code)
    return redirect(url_for('home.profile'))


@bp.context_processor
def inject_joined_rooms():
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


@bp.route('/profile')
def profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    user = get_user_by_id(user_id)
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))

    return render_template('profile.html', user=user)


@bp.route('/moderation')
def moderation():
    controller = ModerationController()
    return controller.show_moderation()


@bp.route('/profile/update', methods=['POST'])
def update_profile():
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


@bp.route('/profile/avatar', methods=['POST'])
def update_avatar():
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


@bp.route('/create_room', methods=['GET', 'POST'])
def create_room():
    if request.method == 'POST':
        room_name = request.form.get('room_name', '').strip()
        subject_tags = (request.form.get('selected_tags') or '').strip()
        submitted_code = (request.form.get('room_code') or '').strip().upper()
        if len(submitted_code) == 6 and submitted_code.isalnum() and not get_room_by_code(submitted_code):
            code = submitted_code
        else:
            code = _generate_unique_room_code()

        is_private = request.form.get('is_private') == '1'

        new_room = create_room_record(code, room_name or f'Room {code}', is_private, subject_tags)

        user_id = session.get('user_id')
        if user_id:
            _remember_joined_room_for_user(user_id, new_room['id'])
        else:
            _remember_joined_room(code)

        return redirect(url_for('home.chat', room_code=code))

    return render_template('createroom.html', room_code=_generate_unique_room_code())
