from app.controllers.base_controller import BaseController
from app.models.message_vote import MessageVote


class MessageVoteController(BaseController):
    def __init__(self):
        super().__init__()

    def handle(self, message_id, user_id, vote_type):
        if vote_type not in ('upvote', 'downvote'):
            raise ValueError('vote_type must be either upvote or downvote')

        MessageVote.create_or_update_vote(message_id, user_id, vote_type)
        vote_counts = MessageVote.get_vote_count(message_id)
        user_vote = MessageVote.get_user_vote(message_id, user_id)

        return {
            'message_id': message_id,
            'user_id': user_id,
            'vote_type': user_vote,
            'upvotes': vote_counts.get('upvotes', 0),
            'downvotes': vote_counts.get('downvotes', 0),
        }
