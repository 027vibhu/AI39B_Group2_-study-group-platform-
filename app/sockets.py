from flask_socketio import join_room, emit
from app import socketio
from app.models import create_message, get_room_by_code

@socketio.on('join')
def handle_join(data):
    room_code = data.get('room')
    username = data.get('username', 'Guest')
    if room_code:
        join_room(room_code)
        print(f"{username} joined room: {room_code}")
        emit('status', {'msg': f'{username} has entered the room'}, room=room_code)

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
