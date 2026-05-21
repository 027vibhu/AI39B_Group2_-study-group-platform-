from flask import Flask



def create_app():
    app = Flask(__name__)

    # register blueprints
    from .routes import auth as auth_bp
    app.register_blueprint(auth_bp.bp)

    @app.errorhandler(404)
    def page_not_found(e):
        return "PAGE NOT FOUND",404

    return app