from flask import Blueprint, render_template


class StatusRoutes:
    def __init__(self):
        self.bp = Blueprint("status", __name__)

    def register(self):
        self.bp.route("/status")(self.status)
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


# expose module-level blueprint for compatibility
status_bp = StatusRoutes().register()