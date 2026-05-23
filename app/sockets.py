from flask_socketio import join_room, leave_room, emit
from app import socketio, db
from app.models import Room, Message

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
        room = Room.query.filter_by(code=room_code).first()
        if room:
            # Save message to database
            new_message = Message(room_id=room.id, username=username, content=message_content)
            db.session.add(new_message)
            db.session.commit()
            
            print(f"Message from {username} to room {room_code}: {message_content}")
            emit('receive_message', {'message': message_content, 'username': username}, room=room_code)
