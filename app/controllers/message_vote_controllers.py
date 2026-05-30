from flask import request, jsonify

from app.controllers.base_controller import BaseController
from app.models.message_vote_model import MessageVoteModel


class MessageVoteController(BaseController):

    def __init__(self):
        self.vote_model = MessageVoteModel()
        self.vote_model.create_table()

    def upvote_message(self):
        data = request.get_json()

        user_id = data.get("user_id")
        message_id = data.get("message_id")

        self.vote_model.add_vote(
            user_id,
            message_id,
            "upvote"
        )

        votes = self.vote_model.get_vote_count(message_id)

        return jsonify({
            "success": True,
            "message": "Message upvoted successfully",
            "votes": votes
        })

    def downvote_message(self):
        data = request.get_json()

        user_id = data.get("user_id")
        message_id = data.get("message_id")

        self.vote_model.add_vote(
            user_id,
            message_id,
            "downvote"
        )

        votes = self.vote_model.get_vote_count(message_id)

        return jsonify({
            "success": True,
            "message": "Message downvoted successfully",
            "votes": votes
        })