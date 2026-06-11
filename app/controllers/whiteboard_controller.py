import json
from app.models.room import get_room_by_code, get_room_by_id, is_user_in_room, is_user_banned_from_room
from app.models.database import get_user_by_id
from app.models.whiteboard import get_whiteboard_state, save_whiteboard_state, clear_whiteboard_state


class WhiteboardController:
    def _authorize_room_access(self, room, user_id):
        if not room:
            return False
        if room.get('is_private') and not is_user_in_room(user_id, room['id']):
            return False
        return True

    def get_state(self, room_code, user_id):
        room = get_room_by_code(room_code)
        if not room:
            return None, 'Room not found'

        if not self._authorize_room_access(room, user_id):
            return None, 'Access denied'

        stored_state = get_whiteboard_state(room['id'])
        if not stored_state:
            return {'room_code': room_code, 'state': None}, None

        try:
            state = json.loads(stored_state.get('state') or 'null')
        except Exception:
            state = None

        return {
            'room_code': room_code,
            'state': state,
            'updated_at': stored_state.get('updated_at'),
            'updated_by_user_id': stored_state.get('updated_by_user_id'),
            'updated_by_username': stored_state.get('updated_by_username'),
        }, None

    def save_state(self, room_code, user_id, state_payload):
        room = get_room_by_code(room_code)
        if not room:
            return None, 'Room not found'

        if not self._authorize_room_access(room, user_id):
            return None, 'Access denied'

        user = get_user_by_id(user_id)
        if not user:
            return None, 'User not found'

        if is_user_banned_from_room(user.get('username'), room_code, room.get('name')):
            return None, 'You are banned from this room.'

        try:
            state_json = json.dumps(state_payload, ensure_ascii=False)
        except Exception:
            return None, 'Invalid whiteboard state payload'

        save_whiteboard_state(room['id'], state_json, user_id, user.get('username'))
        return {'room_code': room_code, 'state': state_payload}, None

    def clear_state(self, room_code, user_id):
        room = get_room_by_code(room_code)
        if not room:
            return None, 'Room not found'

        if not self._authorize_room_access(room, user_id):
            return None, 'Access denied'

        user = get_user_by_id(user_id)
        if not user:
            return None, 'User not found'

        if is_user_banned_from_room(user.get('username'), room_code, room.get('name')):
            return None, 'You are banned from this room.'

        clear_whiteboard_state(room['id'])
        return {'room_code': room_code, 'state': None}, None
