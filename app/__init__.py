from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from config import Config

socketio = SocketIO()
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    socketio.init_app(app)

    # register blueprints
    from app.routes import home as home_bp
    from app.routes import auth as auth_bp
    app.register_blueprint(home_bp.bp)
    app.register_blueprint(auth_bp.bp)

    # Import sockets and models to register them
    from app import sockets, models

    # Create tables
    with app.app_context():
        db.create_all()

    @app.errorhandler(404)
    def page_not_found(e):
        return "PAGE NOT FOUND",404

    return app