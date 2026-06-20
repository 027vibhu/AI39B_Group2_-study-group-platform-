"""Route tests for the quotes blueprint."""

import unittest

from tests.routes.conftest_app import build_test_app
from tests.support.fixtures import login


class QuotesRoutesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = build_test_app()

    def setUp(self):
        self.client = self.app.test_client()

    def test_requires_login(self):
        self.assertEqual(self.client.get('/api/quote').status_code, 302)

    def test_returns_quote(self):
        login(self.client)
        resp = self.client.get('/api/quote')
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertEqual(body['status'], 'success')
        self.assertIsInstance(body['quote'], str)


if __name__ == '__main__':
    unittest.main()
