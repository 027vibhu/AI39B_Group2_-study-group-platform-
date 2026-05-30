import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.models.database import get_database_connection, ensure_database_exists


def purge_tables():
    ensure_database_exists()
    conn = get_database_connection()
    tables = [
        "message_vote",
        "message_votes",
        "message",
        "user_room",
        "room_presence",
        "room_actions",
        "room",
        "users",
    ]
    try:
        with conn.cursor() as cur:
            for table in tables:
                try:
                    cur.execute(f"DELETE FROM {table}")
                except Exception:
                    pass
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    purge_tables()
    print("OK: data cleared")
