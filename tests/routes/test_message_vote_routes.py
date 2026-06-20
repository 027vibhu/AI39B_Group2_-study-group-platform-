"""Route tests for the message_vote blueprint."""

import unittest
from unittest.mock import patch

from tests.routes.conftest_app import build_test_app
from tests.support.fixtures import login

MV = 'app.controllers.message_vote_controller'


class MessageVoteRoutesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = build_test_app()

    def setUp(self):
        self.client = self.app.test_client()

    def test_requires_login(self):
        resp = self.client.post('/message/upvote', json={'user_id': 1, 'message_id': 3})
        self.assertEqual(resp.status_code, 302)

    @patch(f'{MV}.get_message_by_id', return_value=None)
    @patch(f'{MV}.get_vote_count', return_value={'upvotes': 1, 'downvotes': 0})
    @patch(f'{MV}.create_or_update_vote')
    def test_upvote(self, mock_create, mock_count, mock_msg):
        login(self.client)
        resp = self.client.post('/message/upvote', json={'user_id': 1, 'message_id': 3})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.get_json()['success'])
        mock_create.assert_called_once_with(3, 1, 'upvote')

    @patch(f'{MV}.get_message_by_id', return_value=None)
    @patch(f'{MV}.get_vote_count', return_value={'upvotes': 0, 'downvotes': 0})
    @patch(f'{MV}.remove_vote')
    def test_remove_vote(self, mock_remove, mock_count, mock_msg):
        login(self.client)
        resp = self.client.post('/message/remove_vote', json={'user_id': 1, 'message_id': 3})
        self.assertEqual(resp.status_code, 200)
        mock_remove.assert_called_once_with(3, 1)


if __name__ == '__main__':
    unittest.main()
