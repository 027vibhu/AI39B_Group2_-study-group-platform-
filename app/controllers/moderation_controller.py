
from app.controllers.base_controller import BaseController
from app.models.database import get_user_by_id
from app.models.room import get_joined_rooms_for_user, get_owned_rooms_for_user, get_moderation_log_for_room
from flask import session




class ModerationController(BaseController):
    """Controller for moderation page actions.

    Provides a method to render the moderation view and passes the
    currently logged-in user (if any) to the template.
    """

    def show_moderation(self):
        user_id = self.get_session_user_id()
        current_user = get_user_by_id(user_id) if user_id else None
        can_moderate = False
        owned_rooms = []
        joined_rooms = []
        if current_user:
            role = session.get('role')
            if role in ('admin', 'moderator'):
                can_moderate = True
                owned_rooms = get_owned_rooms_for_user(user_id) or []
                joined_rooms = get_joined_rooms_for_user(user_id) or []
            else:
                # check ownership of any joined rooms
                owned_rooms = get_owned_rooms_for_user(user_id) or []
                for r in owned_rooms:
                    if r.get('owner_id') == user_id:
                        can_moderate = True
                        break

        selected_room_code = None
        room_code = None
        try:
            from flask import request
            room_code = (request.args.get('room_code') or '').strip().upper()
        except Exception:
            room_code = ''

        recent_actions = []
        if room_code:
            recent_actions = get_moderation_log_for_room(room_code, limit=10) or []

        return self.render(
            'moderation.html',
            current_user=current_user,
            can_moderate_any=can_moderate,
            owned_rooms=owned_rooms,
            joined_rooms=joined_rooms,
            selected_room_code=room_code,
            recent_actions=recent_actions,
        )
