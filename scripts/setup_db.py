"""
Create database and application DB user for the project.

Usage (PowerShell example):
$env:DB_ADMIN_USER='root'
$env:DB_ADMIN_PASSWORD='root_password'
$env:APP_DB_USER='study_user'
$env:APP_DB_PASSWORD='strong_password'
python scripts/setup_db.py

The script reads `DB_NAME`, `DB_HOST`, `DB_PORT` from `config.py` if not provided.
"""
import os
import sys
import pymysql
from config import Config

ADMIN_USER = os.environ.get('DB_ADMIN_USER') or Config.DB_USER
ADMIN_PASS = os.environ.get('DB_ADMIN_PASSWORD')
APP_USER = os.environ.get('APP_DB_USER') or 'study_user'
APP_PASS = os.environ.get('APP_DB_PASSWORD') or 'study_password'
DB_NAME = os.environ.get('DB_NAME') or Config.DB_NAME
DB_HOST = os.environ.get('DB_HOST') or Config.DB_HOST
DB_PORT = int(os.environ.get('DB_PORT') or Config.DB_PORT)

if not ADMIN_PASS:
    print("Error: Please set DB_ADMIN_PASSWORD environment variable (the admin/root password).")
    sys.exit(1)

print(f"Connecting to MySQL on {DB_HOST}:{DB_PORT} as admin user '{ADMIN_USER}'...")

try:
    conn = pymysql.connect(
        host=DB_HOST,
        user=ADMIN_USER,
        password=ADMIN_PASS,
        port=DB_PORT,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )
except Exception as e:
    print("Failed to connect to MySQL as admin:", e)
    sys.exit(1)

try:
    with conn.cursor() as cursor:
        print(f"Creating database `{DB_NAME}` if not exists...")
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )

        print(f"Creating/ensuring application DB user '{APP_USER}'...")
        # Create user (if not exists) and set password
        try:
            cursor.execute(
                "CREATE USER IF NOT EXISTS %s@'localhost' IDENTIFIED BY %s",
                (APP_USER, APP_PASS),
            )
        except Exception:
            # Some MySQL versions don't support CREATE USER IF NOT EXISTS with parameterization; fallback
            cursor.execute(f"CREATE USER IF NOT EXISTS '{APP_USER}'@'localhost' IDENTIFIED BY '{APP_PASS}'")

        print(f"Granting privileges on `{DB_NAME}` to '{APP_USER}'@'localhost'...")
        cursor.execute(f"GRANT ALL PRIVILEGES ON `{DB_NAME}`.* TO '{APP_USER}'@'localhost'")
        cursor.execute("FLUSH PRIVILEGES")

    print("Database and user setup completed successfully.")
    print("")
    print("Next steps:")
    print("- Update your environment for running the app, e.g. in PowerShell:")
    print("  $env:DB_USER='{}'".format(APP_USER))
    print("  $env:DB_PASSWORD='{}'".format(APP_PASS))
    print("  python scripts/verify_subject_tag.py")

except Exception as e:
    print("Error during DB setup:", e)
    sys.exit(1)
finally:
    conn.close()
