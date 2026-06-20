"""Fakes for the data layer so model code runs without a real MySQL server.

Two layers exist in the app:

* ``app.models.database.Database`` — a small wrapper used by ``BaseModel`` and by
  the class-based models (Task, StudyHour, ...). ``BaseModel`` imports it lazily
  *inside each method* (``from app.models.database import Database``), so patching
  ``app.models.database.Database`` intercepts every subclass too.
* ``app.models.database.get_database_connection`` — a raw pymysql connection used
  directly by the ``users`` functions and a few ``create_*_table`` helpers, via a
  ``with connection.cursor() as cursor`` context manager.

This module provides fakes + context managers for both.
"""

from contextlib import contextmanager
from unittest.mock import MagicMock, patch


# --------------------------------------------------------------------------- #
#  Database-wrapper fakes (BaseModel / class-based models)
# --------------------------------------------------------------------------- #
def make_fake_db(fetch_one=None, fetch_all=None, execute=1):
    """Return a MagicMock shaped like an ``app.models.database.Database`` instance.

    ``fetch_one``/``fetch_all`` may be a value (returned every call) or a list
    passed as ``side_effect`` for methods that query more than once.
    """
    db = MagicMock(name='Database()')

    if isinstance(fetch_one, (list, tuple)):
        db.fetch_one.side_effect = list(fetch_one)
    else:
        db.fetch_one.return_value = fetch_one

    if isinstance(fetch_all, (list, tuple)) and fetch_all and isinstance(fetch_all[0], (list, tuple)):
        # a list of result-sets -> side_effect for multi-call methods
        db.fetch_all.side_effect = list(fetch_all)
    else:
        db.fetch_all.return_value = [] if fetch_all is None else fetch_all

    if isinstance(execute, (list, tuple)):
        db.execute.side_effect = list(execute)
    else:
        db.execute.return_value = execute

    return db


@contextmanager
def patch_database(fetch_one=None, fetch_all=None, execute=1):
    """Patch ``app.models.database.Database`` so every model call uses a fake.

    Yields the fake instance (the value of ``Database()``), letting tests inspect
    ``fake.execute.call_args`` etc.
    """
    fake = make_fake_db(fetch_one=fetch_one, fetch_all=fetch_all, execute=execute)
    with patch('app.models.database.Database', return_value=fake):
        yield fake


# --------------------------------------------------------------------------- #
#  Raw-connection fakes (users functions, create_*_table helpers)
# --------------------------------------------------------------------------- #
def make_fake_connection(fetchone=None, fetchall=None, lastrowid=1, rowcount=1):
    """Return ``(connection, cursor)`` mocks supporting ``with conn.cursor() as c``."""
    conn = MagicMock(name='connection')
    cursor = MagicMock(name='cursor')

    if isinstance(fetchone, (list, tuple)):
        cursor.fetchone.side_effect = list(fetchone)
    else:
        cursor.fetchone.return_value = fetchone

    cursor.fetchall.return_value = [] if fetchall is None else fetchall
    cursor.lastrowid = lastrowid
    cursor.rowcount = rowcount

    ctx = conn.cursor.return_value
    ctx.__enter__.return_value = cursor
    ctx.__exit__.return_value = False
    return conn, cursor


@contextmanager
def patch_connection(target='app.models.database.get_database_connection',
                     fetchone=None, fetchall=None, lastrowid=1, rowcount=1):
    """Patch a ``get_database_connection`` symbol; yield the ``cursor`` mock."""
    conn, cursor = make_fake_connection(fetchone, fetchall, lastrowid, rowcount)
    with patch(target, return_value=conn):
        yield cursor


# --------------------------------------------------------------------------- #
#  Assertion helpers
# --------------------------------------------------------------------------- #
def sql_of(call):
    """Return the SQL string from a mock call to execute/fetch_one/fetch_all."""
    return call.args[0] if call and call.args else None


def params_of(call):
    """Return the params tuple from a mock call, or None if not supplied."""
    if not call:
        return None
    if len(call.args) > 1:
        return call.args[1]
    return call.kwargs.get('params')


def find_call(mock_method, substring):
    """Return the first recorded call whose SQL contains ``substring`` (else None).

    Useful for models whose method first issues CREATE TABLE statements before the
    statement under test — lets a test target the INSERT/SELECT it cares about.
    """
    for call in mock_method.call_args_list:
        if call.args and substring in call.args[0]:
            return call
    return None
