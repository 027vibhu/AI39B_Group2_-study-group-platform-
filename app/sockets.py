from flask import session, request
from flask_socketio import join_room, emit
from app import socketio
from app.models.message import create_message
from app.models.message_vote import create_or_update_vote, get_vote_count, remove_vote
from app.models.room import get_room_by_code, get_room_by_id, is_user_banned_from_room
from app.models.message import get_message_by_id
from app.models.presence_model import set_user_online, set_user_offline, get_online_users, get_offline_users
from app.models.join_leave_notification import add_join_leave_notification

# Track joined sockets so disconnect can update presence
_active_presence = {}

def _broadcast_presence(room_code, room_id):
    online = get_online_users(room_id)
    offline = get_offline_users(room_id)
    emit(
        'presence_update',
        {
            'online': online,
            'offline': offline,
        },
        room=room_code,
    )


@socketio.on('join')
def handle_join(data):
    room_code = data.get('room')
    user_id = session.get('user_id')
    if not user_id:
        emit('moderation_action', {'action': 'auth_required', 'room_code': room_code, 'message': 'Login required.'})
        return

    username = data.get('username') or ''
    if not room_code:
        return

    room = get_room_by_code(room_code)
    if not room:
        return

    if is_user_banned_from_room(username, room_code, room.get('name')):
        emit(
            'moderation_action',
            {
                'action': 'ban',
                'room_code': room_code,
                'username': username,
                'message': 'You are banned from this room.',
            },
        )
        return

    join_room(room_code)
    set_user_online(user_id, room['id'], username)
    add_join_leave_notification(
        room['id'],
        user_id,
        username,
        'join',
        f'{username} has entered the room',
    )
    _active_presence[request.sid] = {
        'user_id': user_id,
        'room_id': room['id'],
        'username': username,
        'room_code': room_code,
    }

    print(f"{username} joined room: {room_code}")
    emit('notification_update', {
        'room_code': room_code,
        'username': username,
        'action_type': 'join',
        'message': f'{username} has entered the room',
    }, room=room_code)
    emit('status', {'msg': f'{username} has entered the room', 'username': username}, room=room_code)
    _broadcast_presence(room_code, room['id'])


@socketio.on('disconnect')
def handle_disconnect():
    presence = _active_presence.pop(request.sid, None)
    if not presence:
        return

    set_user_offline(presence['user_id'], presence['room_id'], presence['username'])
    add_join_leave_notification(
        presence['room_id'],
        presence['user_id'],
        presence['username'],
        'leave',
        f"{presence['username']} has left the room",
    )
    emit('notification_update', {
        'room_code': presence['room_code'],
        'username': presence['username'],
        'action_type': 'leave',
        'message': f"{presence['username']} has left the room",
    }, room=presence['room_code'])
    emit(
        'status',
        {'msg': f"{presence['username']} has left the room", 'username': presence['username']},
        room=presence['room_code'],
    )
    _broadcast_presence(presence['room_code'], presence['room_id'])

@socketio.on('send_message')
def handle_send_message(data):
    room_code = data.get('room')
    message_content = data.get('message')
    user_id = session.get('user_id')
    if not user_id:
        emit('moderation_action', {'action': 'auth_required', 'room_code': room_code, 'message': 'Login required.'})
        return

    username = data.get('username') or ''
    if room_code and message_content:
        room = get_room_by_code(room_code)
        if room:
            if is_user_banned_from_room(username, room_code, room.get('name')):
                emit(
                    'moderation_action',
                    {
                        'action': 'ban',
                        'room_code': room_code,
                        'username': username,
                        'message': 'You are banned from this room.',
                    },
                )
                return

            # Save message to database
            message_id = create_message(room['id'], username, message_content)
            saved_message = get_message_by_id(message_id)
            time_label = saved_message.get('time_label') if saved_message else ''

            print(f"Message from {username} to room {room_code}: {message_content}")
            emit('receive_message', {
                'message': message_content,
                'username': username,
                'message_id': message_id,
                'time_label': time_label,
            }, room=room_code)


@socketio.on('vote_message')
def handle_vote_message(data):
    user_id = session.get('user_id')
    if not user_id:
        emit('vote_error', {'message': 'Authentication required'})
        return

    message_id = data.get('message_id')
    vote_type = data.get('vote_type')
    action = data.get('action') or 'vote'

    if not message_id:
        emit('vote_error', {'message': 'message_id is required'})
        return

    msg = get_message_by_id(message_id)
    if not msg:
        emit('vote_error', {'message': 'Message not found'})
        return

    room = get_room_by_id(msg.get('room_id'))
    if not room or not room.get('code'):
        emit('vote_error', {'message': 'Room not found'})
        return

    if action == 'remove_vote':
        remove_vote(message_id, user_id)
    else:
        if vote_type not in ('upvote', 'downvote'):
            emit('vote_error', {'message': 'Invalid vote type'})
            return
        create_or_update_vote(message_id, user_id, vote_type)

    votes = get_vote_count(message_id)
    payload = {
        'message_id': message_id,
        'upvotes': votes.get('upvotes', 0),
        'downvotes': votes.get('downvotes', 0),
        'room_code': room.get('code'),
        'actor_user_id': user_id,
        'vote_type': None if action == 'remove_vote' else vote_type,
        'action': action,
    }
    emit('vote_update', payload, room=room.get('code'))


@socketio.on('send_file')
def handle_send_file(data):
    room_code = data.get('room')
    filename = data.get('filename')
    file_data_url = data.get('data')
    username = data.get('username') or ''

    if not room_code or not filename or not file_data_url:
        return

    room = get_room_by_code(room_code)
    if not room:
        return

    if is_user_banned_from_room(username, room_code, room.get('name')):
        return

    try:
        header, encoded = file_data_url.split(",", 1)
        import base64
        file_bytes = base64.b64decode(encoded)
    except Exception as e:
        print(f"Error decoding base64 file data: {e}")
        return

    # Check size constraint (25MB)
    if len(file_bytes) > 25 * 1024 * 1024:
        print("File too large via socket upload")
        return

    import os
    _, ext = os.path.splitext(filename)
    ext = ext.lower()
    from app.routes.home import ALLOWED_SHARED_FILE_EXTENSIONS
    if ext not in ALLOWED_SHARED_FILE_EXTENSIONS:
        print(f"File extension {ext} not allowed")
        return

    from werkzeug.utils import secure_filename
    secured_name = secure_filename(filename)
    if not secured_name:
        secured_name = "file" + ext

    import uuid
    stored_filename = f"{uuid.uuid4().hex}{ext}"

    from flask import current_app
    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'shared_files')
    os.makedirs(upload_dir, exist_ok=True)
    saved_path = os.path.join(upload_dir, stored_filename)

    with open(saved_path, 'wb') as f:
        f.write(file_bytes)

    mime_type = 'application/octet-stream'
    if "data:" in header and ";base64" in header:
        mime_type = header.split(";")[0].replace("data:", "")

    from app.models.shared_file import create_shared_file
    file_id = create_shared_file(
        room['id'],
        username,
        secured_name,
        stored_filename,
        mime_type,
        len(file_bytes)
    )

    if not file_id:
        return

    # Send a message to the chat stream referencing this file
    is_image = mime_type.startswith('image/')
    if is_image:
        message_content = f'<img src="/files/{file_id}/view" class="message-image">'
    else:
        message_content = f'<a href="/files/{file_id}/download" download="{secured_name}"><i class="fa-solid fa-file-arrow-down" style="margin-right: 6px;"></i>{secured_name}</a>'

    message_id = create_message(room['id'], username, message_content)
    saved_message = get_message_by_id(message_id)
    time_label = saved_message.get('time_label') if saved_message else ''

    emit('receive_message', {
        'message': message_content,
        'username': username,
        'message_id': message_id,
        'time_label': time_label,
    }, room=room_code)

    emit('file_uploaded', {
        'room_code': room_code,
        'id': file_id,
        'original_filename': secured_name,
        'uploader_username': username,
        'mime_type': mime_type,
        'file_size': len(file_bytes),
        'download_url': f'/files/{file_id}/download',
        'view_url': f'/files/{file_id}/view'
    }, room=room_code)
