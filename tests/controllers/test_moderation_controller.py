"""Unit tests for ModerationController.show_moderation."""

import unittest
from unittest.mock import patch

from flask import session

from tests.support import make_controller_app
from tests.support.fixtures import user_row, room_row


class ModerationTestBase(unittest.TestCase):
    def setUp(self):
        self.app = make_controller_app()
        from app.controllers.moderation_controller import ModerationController
        self.controller = ModerationController()


class TestShowModeration(ModerationTestBase):
    @patch('app.controllers.moderation_controller.BaseController.render', return_value='page')
    def test_anonymous_user_cannot_moderate(self, mock_render):
        with self.app.test_request_context():
            result = self.controller.show_moderation()
        self.assertEqual(result, 'page')
        self.assertFalse(mock_render.call_args.kwargs['can_moderate_any'])

    @patch('app.controllers.moderation_controller.get_joined_rooms_for_user', return_value=[])
    @patch('app.controllers.moderation_controller.get_owned_rooms_for_user', return_value=[room_row()])
    @patch('app.controllers.moderation_controller.get_user_by_id', return_value=user_row())
    @patch('app.controllers.moderation_controller.BaseController.render', return_value='page')
    def test_admin_can_moderate(self, mock_render, mock_user, mock_owned, mock_joined):
        with self.app.test_request_context():
            session['user_id'] = 1
            session['role'] = 'admin'
            self.controller.show_moderation()
        self.assertTrue(mock_render.call_args.kwargs['can_moderate_any'])

    @patch('app.controllers.moderation_controller.get_moderation_log_for_room', return_value=[{'a': 1}])
    @patch('app.controllers.moderation_controller.get_joined_rooms_for_user', return_value=[])
    @patch('app.controllers.moderation_controller.get_owned_rooms_for_user', return_value=[])
    @patch('app.controllers.moderation_controller.get_user_by_id', return_value=user_row())
    @patch('app.controllers.moderation_controller.BaseController.render', return_value='page')
    def test_room_code_loads_log(self, mock_render, mock_user, mock_owned, mock_joined, mock_log):
        with self.app.test_request_context(query_string={'room_code': 'abc123'}):
            session['user_id'] = 1
            session['role'] = 'admin'
            self.controller.show_moderation()
        self.assertEqual(mock_render.call_args.kwargs['selected_room_code'], 'ABC123')
        mock_log.assert_called_once_with('ABC123', limit=10)


if __name__ == '__main__':
    unittest.main()
