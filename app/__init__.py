from flask import Flask



def create_app():
    app = Flask(__name__)

    # register blueprints
    from app.routes import home as home_bp
    from app.routes import auth as auth_bp
    app.register_blueprint(home_bp.bp)
    app.register_blueprint(auth_bp.bp)

    @app.errorhandler(404)
    def page_not_found(e):
        return "PAGE NOT FOUND",404

    return app