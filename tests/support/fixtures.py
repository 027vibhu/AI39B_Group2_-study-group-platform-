"""Canonical sample rows and a login helper for the test suite."""


def user_row(**overrides):
    row = {
        'id': 1,
        'username': 'alice',
        'email': 'alice@example.com',
        'password_hash': 'hashed',
        'avatar_url': 'images/default_user_icon.jpg',
        'first_name': 'Alice',
        'last_name': 'A',
        'school': 'Uni',
        'address': '',
        'bio': '',
        'role': 'user',
        'is_active': 1,
        'deactivated_at': None,
        'created_at': '2026-01-01 00:00:00',
    }
    row.update(overrides)
    return row


def room_row(**overrides):
    row = {
        'id': 10,
        'code': 'ABC123',
        'name': 'Study Room',
        'is_private': 0,
        'subject_tags': 'math',
        'owner_id': 1,
        'created_at': '2026-01-01 00:00:00',
    }
    row.update(overrides)
    return row


def note_row(**overrides):
    row = {
        'id': 5,
        'user_id': 1,
        'title': 'Photosynthesis',
        'pdf_url': 'uploads/notes/abc.pdf',
        'description': 'notes',
        'content_text': None,
        'content_images': None,
        'created_at': '2026-01-01 00:00:00',
    }
    row.update(overrides)
    return row


def task_row(**overrides):
    row = {
        'id': 7,
        'user_id': 1,
        'title': 'Read chapter 1',
        'description': '',
        'status': 'todo',
        'priority': 'medium',
        'due_date': None,
        'is_done': 0,
        'created_at': '2026-01-01 00:00:00',
    }
    row.update(overrides)
    return row


def message_row(**overrides):
    row = {
        'id': 3,
        'room_id': 10,
        'username': 'alice',
        'content': 'hello',
        'timestamp': '2026-01-01 09:00:00',
    }
    row.update(overrides)
    return row


def login(client, user_id=1, username='alice', email='alice@example.com', role='user'):
    """Set a logged-in session on a Flask test client."""
    with client.session_transaction() as sess:
        sess['user_id'] = user_id
        sess['username'] = username
        sess['email'] = email
        sess['role'] = role
