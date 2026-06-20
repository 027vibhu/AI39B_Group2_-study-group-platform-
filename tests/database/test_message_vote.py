"""Unit tests for the MessageVote model."""

import unittest
from unittest.mock import patch

from tests.support import make_fake_db, params_of, find_call
from app.models.message_vote import MessageVote


class MessageVoteTestBase(unittest.TestCase):
    def setUp(self):
        p = patch('app.models.message_vote.ensure_database_exists')
        p.start()
        self.addCleanup(p.stop)
        self.db = make_fake_db()
        p2 = patch('app.models.database.Database', return_value=self.db)
        p2.start()
        self.addCleanup(p2.stop)
        self.model = MessageVote()


class TestVoteWrite(MessageVoteTestBase):
    def test_create_or_update_vote(self):
        self.model.create_or_update_vote(3, 1, 'upvote')
        insert = find_call(self.db.execute, 'INSERT INTO message_vote')
        self.assertIsNotNone(insert)
        self.assertEqual(params_of(insert), (3, 1, 'upvote'))

    def test_remove_vote(self):
        self.model.remove_vote(3, 1)
        delete = find_call(self.db.execute, 'DELETE FROM message_vote')
        self.assertEqual(params_of(delete), (3, 1))


class TestVoteRead(MessageVoteTestBase):
    def test_get_vote_count(self):
        self.db.fetch_one.return_value = {'upvotes': 3, 'downvotes': 1}
        self.assertEqual(self.model.get_vote_count(3), {'upvotes': 3, 'downvotes': 1})

    def test_get_vote_count_defaults_when_empty(self):
        self.db.fetch_one.return_value = None
        self.assertEqual(self.model.get_vote_count(3), {'upvotes': 0, 'downvotes': 0})

    def test_get_user_vote(self):
        self.db.fetch_one.return_value = {'vote_type': 'downvote'}
        self.assertEqual(self.model.get_user_vote(3, 1), 'downvote')

    def test_get_user_vote_none(self):
        self.db.fetch_one.return_value = None
        self.assertIsNone(self.model.get_user_vote(3, 1))


if __name__ == '__main__':
    unittest.main()
