"""Route tests for the status blueprint."""

import unittest

from tests.routes.conftest_app import build_test_app
from tests.support.fixtures import login


class StatusRoutesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = build_test_app()

    def setUp(self):
        self.client = self.app.test_client()

    def test_requires_login(self):
        self.assertEqual(self.client.get('/status').status_code, 302)

    def test_renders_when_logged_in(self):
        login(self.client)
        self.assertEqual(self.client.get('/status').status_code, 200)


if __name__ == '__main__':
    unittest.main()
