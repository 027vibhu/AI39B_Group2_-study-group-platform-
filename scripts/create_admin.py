"""
Ensure the single owner/admin account exists.

The admin account is created automatically when the app starts, so you normally
do not need this script. Run it only if you want to (re)create the owner account
without starting the server:

  python scripts/create_admin.py

Credentials come from config.py / environment (ADMIN_USERNAME, ADMIN_EMAIL,
ADMIN_PASSWORD). By default the owner is username 'admin'. There is exactly one
admin; this script will not create any additional admins.
"""
import os
import sys

# Make sure the project root is importable when run as `python scripts/create_admin.py`.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from app.models.database import ensure_admin_user


def main():
    ensure_admin_user()
    print(f"Owner/admin account ensured: username '{Config.ADMIN_USERNAME}'.")
    print("Log in at /login with that username and the configured password.")


if __name__ == "__main__":
    main()
