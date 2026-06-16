from flask import Blueprint

from app.controllers.resource_vote_controller import ResourceVoteController


class ResourceVoteRoutes:
    def __init__(self):
        self.bp = Blueprint("resource_vote", __name__)
        self.controller = ResourceVoteController()

    def register(self):
        self.bp.route("/resource/upvote", methods=["POST"])(self.upvote_resource)
        self.bp.route("/resource/downvote", methods=["POST"])(self.downvote_resource)
        self.bp.route("/resource/remove_vote", methods=["POST"])(self.remove_vote)
        self.bp.route("/resource/votes", methods=["POST"])(self.get_resource_votes)
        return self.bp

    def upvote_resource(self):
        return self.controller.upvote_resource()

    def downvote_resource(self):
        return self.controller.downvote_resource()

    def remove_vote(self):
        return self.controller.remove_vote()

    def get_resource_votes(self):
        return self.controller.get_resource_votes()


# expose module-level blueprint for compatibility
resource_vote_bp = ResourceVoteRoutes().register()
