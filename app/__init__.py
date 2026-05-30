from flask import Flask
from flask_socketio import SocketIO
from config import Config
from app.routes.roomroutes import room_bp

socketio = SocketIO()

def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    socketio.init_app(app)
    from app.routes import home as home_bp
    from app.routes import auth as auth_bp
    from app.routes.status import status_bp
    from app.routes.message_vote_routes import message_vote_bp

    app.register_blueprint(home_bp.bp)
    app.register_blueprint(auth_bp.bp)
    app.register_blueprint(room_bp)
    app.register_blueprint(status_bp)
    app.register_blueprint(message_vote_bp)

    from app import sockets, models
    from app.models.database import create_users_table
    from app.models.room import create_rooms_table, create_user_rooms_table
    from app.models.message import create_messages_table
    from app.models.message_vote import MessageVote
    from app.models.message_vote_model import MessageVoteModel
    from app.models.presence_model import room_presence_model

    with app.app_context():
        create_users_table()
        create_rooms_table()
        create_user_rooms_table()
        create_messages_table()
        MessageVote.ensure_table_exists()
        MessageVoteModel().create_table()
        room_presence_model.create_room_presence_table()

    @app.errorhandler(404)
    def page_not_found(e):
        return "PAGE NOT FOUND", 404

    return app
