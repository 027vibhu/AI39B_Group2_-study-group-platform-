from flask import Flask
from flask_socketio import SocketIO
from config import Config

socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    socketio.init_app(app)

    # register blueprints
    from app.routes import home as home_bp
    from app.routes import auth as auth_bp
    from app.routes import subject_tags as subject_tags_bp
    app.register_blueprint(home_bp.bp)
    app.register_blueprint(auth_bp.bp)
    app.register_blueprint(subject_tags_bp.bp)

    # Import sockets and models to register them
    from app import sockets, models

    # Ensure MySQL tables exist
    from app.models.database import create_users_table
    from app.models.room import create_rooms_table, create_user_rooms_table
    from app.models.message import create_messages_table
    from app.models.subject_tag import SubjectTagModel

    with app.app_context():
        create_users_table()
        create_rooms_table()
        create_user_rooms_table()
        create_messages_table()
        SubjectTagModel.create_subject_tags_table()
        SubjectTagModel.create_room_subject_tags_table()

    @app.errorhandler(404)
    def page_not_found(e):
        return "PAGE NOT FOUND",404

    return app