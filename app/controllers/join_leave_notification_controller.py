from app.controllers.base_controller import BaseController


class JoinLeaveNotificationController(BaseController):
    def __init__(self):
        super().__init__()
        try:
            import app.models.join_leave_notification as notification_mod
        except Exception:
            notification_mod = None

        self._notification_mod = notification_mod
        if notification_mod and hasattr(notification_mod, 'JoinLeaveNotificationModel'):
            self.notification_model = notification_mod.JoinLeaveNotificationModel()
        else:
            self.notification_model = None

    def create_notifications_table(self):
        if self.notification_model and hasattr(self.notification_model, 'create_table'):
            return self.notification_model.create_table()

        if self._notification_mod and hasattr(self._notification_mod, 'create_join_leave_notifications_table'):
            return self._notification_mod.create_join_leave_notifications_table()

        return None

    def add_notification(self, room_id, user_id, username, action_type, message=None):
        if self.notification_model and hasattr(self.notification_model, 'add_notification'):
            return self.notification_model.add_notification(room_id, user_id, username, action_type, message)

        if self._notification_mod and hasattr(self._notification_mod, 'add_join_leave_notification'):
            return self._notification_mod.add_join_leave_notification(room_id, user_id, username, action_type, message)

        return None

    def get_notifications(self, room_id, limit=50):
        if self.notification_model and hasattr(self.notification_model, 'get_room_notifications'):
            return self.notification_model.get_room_notifications(room_id, limit)

        if self._notification_mod and hasattr(self._notification_mod, 'get_join_leave_notifications'):
            return self._notification_mod.get_join_leave_notifications(room_id, limit)

        return []
