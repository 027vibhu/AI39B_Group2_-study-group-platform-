"""Unit tests for JoinLeaveNotificationController (delegates to model)."""

import unittest
from unittest.mock import MagicMock

from app.controllers.join_leave_notification_controller import JoinLeaveNotificationController


class TestJoinLeaveNotificationController(unittest.TestCase):
    def setUp(self):
        self.controller = JoinLeaveNotificationController()
        # Replace whatever the __init__ wired up with a controllable fake model.
        self.controller.notification_model = MagicMock()

    def test_add_notification_delegates(self):
        self.controller.notification_model.add_notification.return_value = 11
        result = self.controller.add_notification(10, 1, 'alice', 'join', 'hello')
        self.assertEqual(result, 11)
        self.controller.notification_model.add_notification.assert_called_once_with(
            10, 1, 'alice', 'join', 'hello'
        )

    def test_get_notifications_delegates(self):
        self.controller.notification_model.get_room_notifications.return_value = [{'id': 1}]
        result = self.controller.get_notifications(10, limit=20)
        self.assertEqual(result, [{'id': 1}])
        self.controller.notification_model.get_room_notifications.assert_called_once_with(10, 20)

    def test_graceful_when_no_model(self):
        # When neither a model nor module is available, methods no-op safely.
        self.controller.notification_model = None
        self.controller._notification_mod = None
        self.assertIsNone(self.controller.add_notification(1, 1, 'a', 'join'))
        self.assertEqual(self.controller.get_notifications(1), [])


if __name__ == '__main__':
    unittest.main()
