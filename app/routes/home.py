from flask import Blueprint, render_template

bp = Blueprint('home', __name__)


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/join_room')
def join_room():
    return render_template('join_room.html')
