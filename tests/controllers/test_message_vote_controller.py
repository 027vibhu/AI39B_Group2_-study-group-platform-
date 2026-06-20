"""Unit tests for MessageVoteController (vote functions + lazy socketio emit)."""

import unittest
from unittest.mock import patch

from tests.support import make_controller_app
from tests.support.fixtures import message_row, room_row


class MessageVoteTestBase(unittest.TestCase):
    def setUp(self):
        self.app = make_controller_app()
        from app.controllers.message_vote_controller import MessageVoteController
        self.controller = MessageVoteController()


class TestHandleVote(MessageVoteTestBase):
    @patch('app.controllers.message_vote_controller.get_room_by_id', return_value=None)
    @patch('app.controllers.message_vote_controller.get_message_by_id', return_value=None)
    @patch('app.controllers.message_vote_controller.get_vote_count',
           return_value={'upvotes': 3, 'downvotes': 1})
    @patch('app.controllers.message_vote_controller.create_or_update_vote')
    def test_upvote_success(self, mock_create, mock_count, mock_msg, mock_room):
        with self.app.test_request_context(json={'user_id': 1, 'message_id': 3}):
            resp = self.controller.upvote_message()
        body = resp.get_json()
        self.assertTrue(body['success'])
        self.assertEqual(body['votes']['upvotes'], 3)
        mock_create.assert_called_once_with(3, 1, 'upvote')

    @patch('app.controllers.message_vote_controller.get_vote_count', return_value={})
    @patch('app.controllers.message_vote_controller.create_or_update_vote')
    def test_invalid_vote_type_400(self, mock_create, mock_count):
        with self.app.test_request_context(json={'user_id': 1, 'message_id': 3}):
            resp, status = self.controller._handle_vote('sideways')
        self.assertEqual(status, 400)
        mock_create.assert_not_called()


class TestRemoveVote(MessageVoteTestBase):
    @patch('app.controllers.message_vote_controller.get_message_by_id', return_value=None)
    @patch('app.controllers.message_vote_controller.get_vote_count',
           return_value={'upvotes': 0, 'downvotes': 0})
    @patch('app.controllers.message_vote_controller.remove_vote')
    def test_remove(self, mock_remove, mock_count, mock_msg):
        with self.app.test_request_context(json={'user_id': 1, 'message_id': 3}):
            resp = self.controller.remove_vote()
        self.assertTrue(resp.get_json()['success'])
        mock_remove.assert_called_once_with(3, 1)


class TestHandleMethod(MessageVoteTestBase):
    def test_invalid_vote_type_raises(self):
        with self.assertRaises(ValueError):
            self.controller.handle(3, 1, 'nope')

    @patch('app.controllers.message_vote_controller.get_message_by_id')
    @patch('app.controllers.message_vote_controller.get_room_by_id')
    @patch('app.controllers.message_vote_controller.get_user_vote', return_value='upvote')
    @patch('app.controllers.message_vote_controller.get_vote_count',
           return_value={'upvotes': 2, 'downvotes': 0})
    @patch('app.controllers.message_vote_controller.create_or_update_vote')
    def test_handle_broadcasts_and_returns_summary(self, mock_create, mock_count,
                                                   mock_uservote, mock_room, mock_msg):
        mock_msg.return_value = message_row(room_id=10)
        mock_room.return_value = room_row(code='ABC123')
        # Patch the lazily-imported socketio (from app import socketio).
        with patch('app.socketio') as mock_socketio:
            result = self.controller.handle(3, 1, 'upvote')
            mock_socketio.emit.assert_called_once()
        self.assertEqual(result['upvotes'], 2)
        self.assertEqual(result['vote_type'], 'upvote')


if __name__ == '__main__':
    unittest.main()
