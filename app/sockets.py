from flask import session, request
from flask_socketio import disconnect, join_room, emit
from app import socketio
from app.models import (
    create_message,
    get_room_by_code,
    set_user_online,
    set_user_offline,
    get_online_users,
    get_offline_users,
)

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
    username = data.get('username', 'Guest')
    if not room_code:
        return

    room = get_room_by_code(room_code)
    if not room:
        return

    user_id = session.get('user_id') or 0
    join_room(room_code)
    set_user_online(user_id, room['id'], username)
    _active_presence[request.sid] = {
        'user_id': user_id,
        'room_id': room['id'],
        'username': username,
        'room_code': room_code,
    }

    print(f"{username} joined room: {room_code}")
    emit('status', {'msg': f'{username} has entered the room', 'username': username}, room=room_code)
    _broadcast_presence(room_code, room['id'])


@socketio.on('disconnect')
def handle_disconnect():
    presence = _active_presence.pop(request.sid, None)
    if not presence:
        return

    set_user_offline(presence['user_id'], presence['room_id'], presence['username'])
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
    username = data.get('username', 'Guest')
    if room_code and message_content:
        room = get_room_by_code(room_code)
        if room:
            # Save message to database
            message_id = create_message(room['id'], username, message_content)

            print(f"Message from {username} to room {room_code}: {message_content}")
            emit('receive_message', {
                'message': message_content,
                'username': username,
                'message_id': message_id,
            }, room=room_code)
