from flask import Blueprint, render_template, jsonify
from app.controllers.database_setup_controller import DatabaseSetupController


class StatusRoutes:
    def __init__(self):
        self.bp = Blueprint("status", __name__)

    def register(self):
        self.bp.route("/status")(self.status)
        self.bp.route("/notift")(self.notift)
        self.bp.route("/initialize_database", methods=["POST"])(self.initialize_database)
        return self.bp

    def status(self):
        members = [
            {"name": "Alice", "is_online": True},
            {"name": "Brian", "is_online": False},
            {"name": "Clara", "is_online": True},
        ]

        return render_template(
            "status.html",
            members=members
        )

    def notift(self):
        return render_template('notift.html')

    def initialize_database(self):
        controller = DatabaseSetupController()
        result = controller.initialize_database()
        return jsonify(result)


# expose module-level blueprint for compatibility
status_bp = StatusRoutes().register()