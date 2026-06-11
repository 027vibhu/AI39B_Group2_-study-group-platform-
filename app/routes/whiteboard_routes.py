import json
from flask import Blueprint, jsonify, request, session
from app import socketio
from app.controllers.whiteboard_controller import WhiteboardController

whiteboard_bp = Blueprint('whiteboard', __name__)
controller = WhiteboardController()


@whiteboard_bp.route('/api/rooms/<room_code>/whiteboard/state', methods=['GET'])
def get_whiteboard_state(room_code):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': 'Authentication required.'}), 401

    state_data, error = controller.get_state(room_code, user_id)
    if error:
        status_code = 403 if error == 'Access denied' else 404
        return jsonify({'status': 'error', 'message': error}), status_code

    return jsonify({'status': 'success', 'data': state_data}), 200


@whiteboard_bp.route('/api/rooms/<room_code>/whiteboard/state', methods=['POST'])
def save_whiteboard_state_route(room_code):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': 'Authentication required.'}), 401

    payload = request.get_json(silent=True)
    if not payload or 'state' not in payload:
        return jsonify({'status': 'error', 'message': 'State payload is required.'}), 400

    state_payload = payload['state']
    result, error = controller.save_state(room_code, user_id, state_payload)
    if error:
        status_code = 403 if error in ('Access denied', 'You are banned from this room.') else 404
        return jsonify({'status': 'error', 'message': error}), status_code

    socketio.emit('whiteboard_state', {'room_code': room_code, 'state': state_payload}, room=room_code)
    return jsonify({'status': 'success', 'data': result}), 200


@whiteboard_bp.route('/api/rooms/<room_code>/whiteboard/state', methods=['DELETE'])
def clear_whiteboard_state_route(room_code):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': 'Authentication required.'}), 401

    result, error = controller.clear_state(room_code, user_id)
    if error:
        status_code = 403 if error in ('Access denied', 'You are banned from this room.') else 404
        return jsonify({'status': 'error', 'message': error}), status_code

    socketio.emit('whiteboard_cleared', {'room_code': room_code}, room=room_code)
    return jsonify({'status': 'success', 'data': result}), 200
