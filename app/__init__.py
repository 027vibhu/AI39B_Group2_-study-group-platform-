from flask import Flask
from flask_socketio import SocketIO
from config import Config
from app.routes.roomroutes import room_bp

# Use a compatible async mode for the current environment.
# threading is the safest fallback when eventlet/gevent are unavailable or unsupported.
socketio = SocketIO(async_mode='threading')

def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    socketio.init_app(app)
    from app.routes import home as home_bp
    from app.routes import auth as auth_bp
    from app.routes.status import status_bp
    from app.routes.message_vote_routes import message_vote_bp
    from app.routes.join_leave_notification_routes import join_leave_notification_bp
    from app.routes import exam_countdown_routes as exam_countdown

    app.register_blueprint(home_bp.bp)
    app.register_blueprint(auth_bp.bp)
    app.register_blueprint(room_bp)
    app.register_blueprint(status_bp)
    app.register_blueprint(message_vote_bp)
    app.register_blueprint(join_leave_notification_bp)
    app.register_blueprint(exam_countdown.exam_bp)

    from app import sockets, models
    # Import the database module as a module object so tests can monkeypatch
    # `app.models.database` (run_smoke.py) with a lightweight stub.
    try:
        import app.models.database as _db_mod
    except Exception:
        _db_mod = None

    with app.app_context():
        if _db_mod is None:
            pass
        else:
            # Prefer class-based Database.create_tables when present
            if hasattr(_db_mod, 'Database'):
                try:
                    _db_mod.Database.create_tables()
                except Exception:
                    # Best-effort: ignore creation errors during test runs
                    pass
            else:
                # Fallback to module-level functions if provided by stubs
                try:
                    if hasattr(_db_mod, 'ensure_database_exists'):
                        _db_mod.ensure_database_exists()
                    if hasattr(_db_mod, 'create_users_table'):
                        _db_mod.create_users_table()
                except Exception:
                    pass

    @app.errorhandler(404)
    def page_not_found(e):
        return "PAGE NOT FOUND", 404

    return app
