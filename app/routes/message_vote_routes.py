from flask import Blueprint

from app.controllers.message_vote_controllers import MessageVoteController


message_vote_bp = Blueprint(
    "message_vote",
    __name__
)

vote_controller = MessageVoteController()


@message_vote_bp.route("/message/upvote", methods=["POST"])
def upvote_message():
    return vote_controller.upvote_message()


@message_vote_bp.route("/message/downvote", methods=["POST"])
def downvote_message():
    return vote_controller.downvote_message()