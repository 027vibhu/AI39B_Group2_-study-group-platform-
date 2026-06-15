from flask import request, jsonify

from app.controllers.base_controller import BaseController
from app.models.resource_vote import create_or_update_vote, get_vote_count, get_user_vote, remove_vote


class ResourceVoteController(BaseController):
    def __init__(self):
        super().__init__()

    def _broadcast_vote_update(self, resource_id, votes, room_code=None, user_vote=None):
        try:
            from app import socketio
            payload = {
                'resource_id': resource_id,
                'upvotes': votes.get('upvotes', 0),
                'downvotes': votes.get('downvotes', 0),
            }
            if room_code:
                payload['room_code'] = room_code
            if user_vote is not None:
                payload['user_vote'] = user_vote

            print(f"[resource_vote_broadcast] resource={resource_id} payload={payload}")
            if room_code:
                socketio.emit('resource_vote_update', payload, namespace='/', to=room_code)
            else:
                socketio.emit('resource_vote_update', payload, namespace='/')
        except Exception as exc:
            print(f"[resource_vote_broadcast] failed: {exc}")

    def _handle_vote(self, vote_type):
        data = request.get_json() or {}

        user_id = data.get("user_id")
        resource_id = data.get("resource_id")
        room_code = data.get("room_code")

        if not user_id or not resource_id:
            return jsonify({"success": False, "message": "user_id and resource_id are required"}), 400

        if vote_type not in ("upvote", "downvote"):
            return jsonify({"success": False, "message": "Invalid vote type"}), 400

        create_or_update_vote(resource_id, user_id, vote_type)
        votes = get_vote_count(resource_id)
        user_vote = get_user_vote(resource_id, user_id)

        # Broadcast update to clients
        self._broadcast_vote_update(resource_id, votes, room_code, user_vote)

        return jsonify({
            "success": True,
            "message": f"Resource {vote_type}d successfully",
            "votes": votes,
            "user_vote": user_vote,
        })

    def upvote_resource(self):
        return self._handle_vote("upvote")

    def downvote_resource(self):
        return self._handle_vote("downvote")

    def remove_vote(self):
        data = request.get_json() or {}
        user_id = data.get("user_id")
        resource_id = data.get("resource_id")
        room_code = data.get("room_code")

        if not user_id or not resource_id:
            return jsonify({"success": False, "message": "user_id and resource_id are required"}), 400
        
        remove_vote(resource_id, user_id)
        votes = get_vote_count(resource_id)

        # Broadcast update to clients
        self._broadcast_vote_update(resource_id, votes, room_code)

        return jsonify({
            "success": True,
            "message": "Vote removed successfully",
            "votes": votes,
        })

    def get_resource_votes(self):
        data = request.get_json() or {}
        resource_id = data.get("resource_id")
        user_id = data.get("user_id")

        if not resource_id:
            return jsonify({"success": False, "message": "resource_id is required"}), 400

        votes = get_vote_count(resource_id)
        user_vote = get_user_vote(resource_id, user_id) if user_id else None

        return jsonify({
            "success": True,
            "votes": votes,
            "user_vote": user_vote,
        })

    def handle(self, resource_id, user_id, vote_type):
        if vote_type not in ('upvote', 'downvote'):
            raise ValueError('vote_type must be either upvote or downvote')

        create_or_update_vote(resource_id, user_id, vote_type)
        vote_counts = get_vote_count(resource_id)
        user_vote = get_user_vote(resource_id, user_id)

        # Broadcast vote update to other clients
        try:
            self._broadcast_vote_update(resource_id, vote_counts, None, user_vote)
        except Exception:
            # best-effort broadcast; ignore failures
            pass

        return {
            'resource_id': resource_id,
            'user_id': user_id,
            'vote_type': user_vote,
            'upvotes': vote_counts.get('upvotes', 0),
            'downvotes': vote_counts.get('downvotes', 0),
        }
