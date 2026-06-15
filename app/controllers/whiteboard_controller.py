import json
import random

from app.models.database import get_user_by_id
from app.models.whiteboard import (
    create_whiteboard,
    get_whiteboard_by_code,
    add_whiteboard_member,
    is_user_in_whiteboard,
    get_whiteboards_for_user,
    get_whiteboard_state,
    save_whiteboard_state,
    clear_whiteboard_state,
)


class WhiteboardController:
    def _generate_unique_code(self):
        while True:
            code = str(random.randint(100000, 999999))
            if not get_whiteboard_by_code(code):
                return code

    def _authorize(self, board, user_id):
        """A user may access a board if they are a member of it."""
        if not board:
            return False
        return is_user_in_whiteboard(user_id, board['id'])

    # --- Hub actions ----------------------------------------------------
    def create_board(self, user_id, title=None):
        code = self._generate_unique_code()
        title = (title or '').strip() or f'Whiteboard {code}'
        board = create_whiteboard(code, title, owner_id=user_id)
        add_whiteboard_member(user_id, board['id'])
        return board, None

    def list_boards(self, user_id):
        return get_whiteboards_for_user(user_id), None

    def join_board(self, user_id, code):
        code = (code or '').strip()
        if not code:
            return None, 'A board code is required.'
        board = get_whiteboard_by_code(code)
        if not board:
            return None, 'No whiteboard found with that code.'
        add_whiteboard_member(user_id, board['id'])
        return board, None

    def get_board_for_user(self, user_id, code):
        """Open a board. Boards are open-by-code, so opening one joins it."""
        board = get_whiteboard_by_code(code)
        if not board:
            return None, 'Whiteboard not found'
        # Opening via a shared code grants membership.
        add_whiteboard_member(user_id, board['id'])
        return board, None

    # --- State ----------------------------------------------------------
    def get_state(self, code, user_id):
        board = get_whiteboard_by_code(code)
        if not board:
            return None, 'Whiteboard not found'

        if not self._authorize(board, user_id):
            return None, 'Access denied'

        stored_state = get_whiteboard_state(board['id'])
        if not stored_state:
            return {'code': code, 'state': None}, None

        try:
            state = json.loads(stored_state.get('state') or 'null')
        except Exception:
            state = None

        return {
            'code': code,
            'state': state,
            'updated_at': stored_state.get('updated_at'),
            'updated_by_user_id': stored_state.get('updated_by_user_id'),
            'updated_by_username': stored_state.get('updated_by_username'),
        }, None

    def save_state(self, code, user_id, state_payload):
        board = get_whiteboard_by_code(code)
        if not board:
            return None, 'Whiteboard not found'

        if not self._authorize(board, user_id):
            return None, 'Access denied'

        user = get_user_by_id(user_id)
        if not user:
            return None, 'User not found'

        try:
            state_json = json.dumps(state_payload, ensure_ascii=False)
        except Exception:
            return None, 'Invalid whiteboard state payload'

        save_whiteboard_state(board['id'], state_json, user_id, user.get('username'))
        return {'code': code, 'state': state_payload}, None

    def clear_state(self, code, user_id):
        board = get_whiteboard_by_code(code)
        if not board:
            return None, 'Whiteboard not found'

        if not self._authorize(board, user_id):
            return None, 'Access denied'

        clear_whiteboard_state(board['id'])
        return {'code': code, 'state': None}, None
