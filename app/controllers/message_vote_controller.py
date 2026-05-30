from flask import request, jsonify

from app.controllers.base_controller import BaseController
from app.models.message_vote import create_or_update_vote, get_vote_count, get_user_vote, remove_vote
from app.models.message import get_message_by_id
from app.models.room import get_room_by_id


class MessageVoteController(BaseController):
    def __init__(self):
        super().__init__()

    def _broadcast_vote_update(self, message_id, votes, room_code, user_vote=None):
        try:
            from app import socketio
            payload = {
                'message_id': message_id,
                'upvotes': votes.get('upvotes', 0),
                'downvotes': votes.get('downvotes', 0),
                'room_code': room_code,
            }
            if user_vote is not None:
                payload['user_vote'] = user_vote

            print(f"[vote_broadcast] room={room_code} payload={payload}")
            socketio.emit('vote_update', payload, namespace='/', to=room_code)
        except Exception as exc:
            print(f"[vote_broadcast] failed: {exc}")

    def _handle_vote(self, vote_type):
        data = request.get_json() or {}

        user_id = data.get("user_id")
        message_id = data.get("message_id")

        if vote_type not in ("upvote", "downvote"):
            return jsonify({"success": False, "message": "Invalid vote type"}), 400

        create_or_update_vote(message_id, user_id, vote_type)
        votes = get_vote_count(message_id)

        # Broadcast update to other clients in the room
        try:
            msg = get_message_by_id(message_id)
            if msg:
                room = get_room_by_id(msg.get('room_id'))
                if room and room.get('code'):
                    self._broadcast_vote_update(message_id, votes, room.get('code'))
        except Exception:
            pass

        return jsonify({
            "success": True,
            "message": f"Message {vote_type}d successfully",
            "votes": votes,
        })

    def upvote_message(self):
        return self._handle_vote("upvote")

    def downvote_message(self):
        return self._handle_vote("downvote")

    def remove_vote(self):
        data = request.get_json() or {}
        user_id = data.get("user_id")
        message_id = data.get("message_id")
        
        remove_vote(message_id, user_id)
        votes = get_vote_count(message_id)
        
        # Broadcast update to other clients in the room
        try:
            msg = get_message_by_id(message_id)
            if msg:
                room = get_room_by_id(msg.get('room_id'))
                if room and room.get('code'):
                    self._broadcast_vote_update(message_id, votes, room.get('code'))
        except Exception:
            pass

        return jsonify({
            "success": True,
            "message": "Vote removed successfully",
            "votes": votes,
        })

    def handle(self, message_id, user_id, vote_type):
        if vote_type not in ('upvote', 'downvote'):
            raise ValueError('vote_type must be either upvote or downvote')

        create_or_update_vote(message_id, user_id, vote_type)
        vote_counts = get_vote_count(message_id)
        user_vote = get_user_vote(message_id, user_id)

        # Broadcast vote update to other clients in the room (if message exists)
        try:
            msg = get_message_by_id(message_id)
            if msg:
                room = get_room_by_id(msg.get('room_id'))
                if room and room.get('code'):
                    self._broadcast_vote_update(message_id, vote_counts, room.get('code'), user_vote)
        except Exception:
            # best-effort broadcast; ignore failures
            pass

        return {
            'message_id': message_id,
            'user_id': user_id,
            'vote_type': user_vote,
            'upvotes': vote_counts.get('upvotes', 0),
            'downvotes': vote_counts.get('downvotes', 0),
        }
