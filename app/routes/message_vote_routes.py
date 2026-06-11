from flask import Blueprint

from app.controllers.message_vote_controller import MessageVoteController


class MessageVoteRoutes:
    def __init__(self):
        self.bp = Blueprint("message_vote", __name__)
        self.controller = MessageVoteController()

    def register(self):
        self.bp.route("/message/upvote", methods=["POST"])(self.upvote_message)
        self.bp.route("/message/downvote", methods=["POST"])(self.downvote_message)
        self.bp.route("/message/remove_vote", methods=["POST"])(self.remove_vote)
        return self.bp

    def upvote_message(self):
        return self.controller.upvote_message()

    def downvote_message(self):
        return self.controller.downvote_message()

    def remove_vote(self):
        return self.controller.remove_vote()


# expose module-level blueprint for compatibility
message_vote_bp = MessageVoteRoutes().register()