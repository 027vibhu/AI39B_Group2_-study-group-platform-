"""Shared test helpers (fakes, app factory, fixtures).

Importable as `from tests.support import ...`. These helpers let the suite run
with no MySQL, no network, and no API keys by mocking the data layer.
"""

import os
import sys

# Make the project root importable when tests are run directly.
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tests.support.fake_db import (  # noqa: E402
    make_fake_db,
    patch_database,
    make_fake_connection,
    patch_connection,
    sql_of,
    params_of,
    find_call,
)
from tests.support.app_factory import make_controller_app  # noqa: E402
from tests.support import fixtures  # noqa: E402

__all__ = [
    'make_fake_db',
    'patch_database',
    'make_fake_connection',
    'patch_connection',
    'sql_of',
    'params_of',
    'find_call',
    'make_controller_app',
    'fixtures',
]
