from flask import Blueprint, render_template

status_bp = Blueprint("status", __name__)

@status_bp.route("/status")
def status():

    members = [
        {"name": "Alice", "is_online": True},
        {"name": "Brian", "is_online": False},
        {"name": "Clara", "is_online": True},
    ]

    return render_template(
        "status.html",
        members=members
    )