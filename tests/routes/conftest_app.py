"""Build the real Flask app for test_client tests without needing MySQL.

``create_app()`` calls ``Database.create_tables()`` (which would try to reach
MySQL). We patch it out during construction. Per-request DB access is mocked in
the individual route tests. The built app is cached so the (relatively heavy)
factory runs once per process.
"""

from unittest.mock import patch

import tests.support  # noqa: F401  (ensures project root is on sys.path)

_app = None


def build_test_app():
    global _app
    if _app is None:
        with patch('app.models.database.Database.create_tables'):
            from app import create_app
            _app = create_app()
        _app.config['TESTING'] = True
    return _app


def client():
    return build_test_app().test_client()
