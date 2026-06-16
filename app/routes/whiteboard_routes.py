import os
import uuid

from flask import Blueprint, jsonify, request, session, current_app, url_for

from app import socketio
from app.controllers.whiteboard_controller import WhiteboardController
from app.routes.home import MAX_SHARED_FILE_SIZE

whiteboard_bp = Blueprint('whiteboard', __name__)
controller = WhiteboardController()

# Image-only whitelist: PDFs are rasterized to PNG client-side before upload,
# so the server only ever receives images. (Intentionally narrower than the
# shared-files whitelist in home.py.)
ALLOWED_WHITEBOARD_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}


@whiteboard_bp.route('/api/whiteboards/<code>/state', methods=['GET'])
def get_whiteboard_state(code):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': 'Authentication required.'}), 401

    state_data, error = controller.get_state(code, user_id)
    if error:
        status_code = 403 if error == 'Access denied' else 404
        return jsonify({'status': 'error', 'message': error}), status_code

    return jsonify({'status': 'success', 'data': state_data}), 200


@whiteboard_bp.route('/api/whiteboards/<code>/state', methods=['POST'])
def save_whiteboard_state_route(code):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': 'Authentication required.'}), 401

    payload = request.get_json(silent=True)
    if not payload or 'state' not in payload:
        return jsonify({'status': 'error', 'message': 'State payload is required.'}), 400

    state_payload = payload['state']
    result, error = controller.save_state(code, user_id, state_payload)
    if error:
        status_code = 403 if error == 'Access denied' else 404
        return jsonify({'status': 'error', 'message': error}), status_code

    socketio.emit('whiteboard_state', {'code': code, 'state': state_payload}, room=code)
    return jsonify({'status': 'success', 'data': result}), 200


@whiteboard_bp.route('/api/whiteboards/<code>/state', methods=['DELETE'])
def clear_whiteboard_state_route(code):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': 'Authentication required.'}), 401

    result, error = controller.clear_state(code, user_id)
    if error:
        status_code = 403 if error == 'Access denied' else 404
        return jsonify({'status': 'error', 'message': error}), status_code

    socketio.emit('whiteboard_cleared', {'code': code}, room=code)
    return jsonify({'status': 'success', 'data': result}), 200


@whiteboard_bp.route('/api/whiteboards/<code>/upload', methods=['POST'])
def upload_whiteboard_image(code):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': 'Authentication required.'}), 401

    # Membership check — reuse the same open-by-code access flow as the board view.
    board, error = controller.get_board_for_user(user_id, code)
    if error:
        status_code = 403 if error == 'Access denied' else 404
        return jsonify({'status': 'error', 'message': error}), status_code

    upload = request.files.get('file')
    if not upload or not upload.filename:
        return jsonify({'status': 'error', 'message': 'No file provided.'}), 400

    _, ext = os.path.splitext(upload.filename)
    ext = ext.lower()
    if ext not in ALLOWED_WHITEBOARD_IMAGE_EXTENSIONS:
        return jsonify({'status': 'error', 'message': f'File type {ext} not allowed.'}), 400

    # Enforce the 25 MB cap without trusting the client: measure the stream.
    upload.stream.seek(0, os.SEEK_END)
    size = upload.stream.tell()
    upload.stream.seek(0)
    if size > MAX_SHARED_FILE_SIZE:
        return jsonify({'status': 'error', 'message': 'File too large (max 25 MB).'}), 400

    # Stored name is a uuid + validated extension, so the client filename never
    # reaches the filesystem — no path-traversal surface.
    stored_filename = f'{uuid.uuid4().hex}{ext}'

    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'whiteboard')
    os.makedirs(upload_dir, exist_ok=True)
    upload.save(os.path.join(upload_dir, stored_filename))

    url = url_for('static', filename=f'uploads/whiteboard/{stored_filename}')
    return jsonify({'status': 'success', 'url': url}), 200
