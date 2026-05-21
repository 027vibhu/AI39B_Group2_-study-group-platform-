from flask import Flask



def create_app():
    app = Flask(__name__)

    @app.errorhandler(404)
    def page_not_found(e):
        return "PAGE NOT FOUND",404
    
    return app