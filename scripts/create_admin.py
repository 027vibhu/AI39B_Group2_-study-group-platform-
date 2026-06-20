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
