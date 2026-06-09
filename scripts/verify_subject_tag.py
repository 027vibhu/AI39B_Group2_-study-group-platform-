"""
Verification script for `subject_tag` support.
Run locally to attempt creating a test room and print the stored row.
This script does not run automatically; run it where your DB is accessible.
"""
import os
import random
import sys

# Ensure the project root is on sys.path so the `app` package can be imported
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.models import create_room, get_room_by_code


def main():
    # Generate a unique-ish 6-digit code for test
    code = str(random.randint(100000, 999999))
    name = f"Test Room {code}"
    subject_tag = "TestSubject"
    is_private = False

    try:
        room = create_room(code, name, subject_tag, is_private)
        print("Created room:")
        print(room)

        fetched = get_room_by_code(code)
        print("Fetched room from DB:")
        print(fetched)

    except Exception as e:
        print("Error while creating or fetching room:", e)
        sys.exit(1)


if __name__ == '__main__':
    main()
