"""A minimal Flask app for controller unit tests.

Controllers call ``url_for(...)`` / ``self.redirect(...)`` / ``render_template(...)``,
so they must run inside an app context with the redirect-target endpoints
registered. This builds a tiny app whose endpoints are no-op stubs — just enough
for ``url_for`` to resolve. ``render_template`` is mocked in individual tests.
"""

from flask import Flask, Blueprint


# Every endpoint a controller may redirect to (blueprint -> endpoint names).
_STUB_ENDPOINTS = {
    'auth': [
        'login', 'logout', 'register', 'reset_password',
        'reactivate_page',
    ],
    'home': [
        'index', 'dashboard', 'profile', 'notes', 'schedule', 'schedule_page',
        'study_flashcards', 'study_hours_page', 'study_streak_page',
        'browse_rooms', 'whiteboard', 'chat',
    ],
    'admin': ['dashboard'],
}


def _stub(*args, **kwargs):
    return ''


def make_controller_app():
    """Return a Flask app with stub endpoints registered for url_for resolution."""
    app = Flask(__name__)
    app.secret_key = 'test-secret-key'
    app.config['TESTING'] = True

    for bp_name, endpoints in _STUB_ENDPOINTS.items():
        bp = Blueprint(bp_name, bp_name)
        for endpoint in endpoints:
            # Extra url_for kwargs (note_id, set_id, ...) become query params,
            # so a parameterless rule is fine for resolving redirects.
            bp.add_url_rule(f'/{bp_name}/{endpoint}', endpoint=endpoint, view_func=_stub)
        app.register_blueprint(bp)

    return app
