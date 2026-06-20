"""Route tests for the whiteboard blueprint (state API)."""

import unittest
from unittest.mock import patch

from tests.routes.conftest_app import build_test_app
from tests.support.fixtures import login
import app.routes.whiteboard_routes as wb_routes


class WhiteboardRoutesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = build_test_app()

    def setUp(self):
        self.client = self.app.test_client()

    def test_requires_login(self):
        # Gate redirects unauthenticated requests before the handler runs.
        self.assertEqual(self.client.get('/api/whiteboards/ABC123/state').status_code, 302)

    def test_get_state_success(self):
        login(self.client)
        with patch.object(wb_routes.controller, 'get_state',
                          return_value=({'code': 'ABC123', 'state': None}, None)):
            resp = self.client.get('/api/whiteboards/ABC123/state')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['status'], 'success')

    def test_get_state_access_denied_403(self):
        login(self.client)
        with patch.object(wb_routes.controller, 'get_state', return_value=(None, 'Access denied')):
            resp = self.client.get('/api/whiteboards/ABC123/state')
        self.assertEqual(resp.status_code, 403)

    def test_save_state_requires_payload_400(self):
        login(self.client)
        resp = self.client.post('/api/whiteboards/ABC123/state', json={})
        self.assertEqual(resp.status_code, 400)

    def test_save_state_success(self):
        login(self.client)
        with patch.object(wb_routes.controller, 'save_state',
                          return_value=({'code': 'ABC123', 'state': {}}, None)):
            with patch.object(wb_routes, 'socketio'):
                resp = self.client.post('/api/whiteboards/ABC123/state', json={'state': {'shapes': []}})
        self.assertEqual(resp.status_code, 200)


if __name__ == '__main__':
    unittest.main()
