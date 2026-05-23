from flask import Blueprint, render_template, redirect, url_for
from app.models import Room, Message
from app import db
import random

bp = Blueprint('home', __name__)


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/join_room')
def join_room():
    return render_template('join_room.html')


@bp.route('/create')
def create():
    # Generate a unique 6-digit code
    while True:
        code = str(random.randint(100000, 999999))
        if not Room.query.filter_by(code=code).first():
            break
    
    new_room = Room(code=code)
    db.session.add(new_room)
    db.session.commit()
    
    return redirect(url_for('home.chat', room_code=code))


@bp.route('/chat/<room_code>')
def chat(room_code):
    room = Room.query.filter_by(code=room_code).first()
    if not room:
        return "Room not found", 404
    
    # Fetch previous messages
    messages = Message.query.filter_by(room_id=room.id).order_by(Message.timestamp.asc()).all()
    
    return render_template('chat.html', room_code=room_code, messages=messages)
