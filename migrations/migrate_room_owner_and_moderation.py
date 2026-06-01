"""Best-effort migration for room ownership and moderation audit tables.

Usage:
    python migrations/migrate_room_owner_and_moderation.py
"""

from app.models.database import ensure_database_exists, get_database_connection


def column_exists(cursor, table_name, column_name):
    cursor.execute(
        "SELECT COUNT(*) AS count FROM information_schema.columns "
        "WHERE table_schema = DATABASE() AND table_name = %s AND column_name = %s",
        (table_name, column_name),
    )
    row = cursor.fetchone()
    return bool(row and row.get('count'))


def table_exists(cursor, table_name):
    cursor.execute(
        "SELECT COUNT(*) AS count FROM information_schema.tables "
        "WHERE table_schema = DATABASE() AND table_name = %s",
        (table_name,),
    )
    row = cursor.fetchone()
    return bool(row and row.get('count'))


def main():
    ensure_database_exists()
    connection = get_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS room ("
                "id INT AUTO_INCREMENT PRIMARY KEY,"
                "owner_id INT NULL,"
                "code VARCHAR(6) NOT NULL UNIQUE,"
                "name VARCHAR(120) NOT NULL DEFAULT '',"
                "is_private TINYINT(1) NOT NULL DEFAULT 0,"
                "subject_tags VARCHAR(255) DEFAULT '',"
                "created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"
                ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
            )

            if not column_exists(cursor, 'room', 'owner_id'):
                cursor.execute("ALTER TABLE room ADD COLUMN owner_id INT NULL AFTER id")

            cursor.execute(
                "CREATE TABLE IF NOT EXISTS room_moderation_log ("
                "id INT AUTO_INCREMENT PRIMARY KEY,"
                "room_id INT NULL,"
                "room_code VARCHAR(6) NOT NULL,"
                "actor_user_id INT NULL,"
                "actor_username VARCHAR(50) NOT NULL,"
                "target_username VARCHAR(50) NOT NULL,"
                "action_type ENUM('kick', 'ban') NOT NULL,"
                "duration_minutes INT NULL,"
                "reason TEXT NULL,"
                "created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
                "INDEX idx_room_moderation_room_code (room_code),"
                "INDEX idx_room_moderation_room_id (room_id),"
                "INDEX idx_room_moderation_target (target_username)"
                ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
            )

            cursor.execute(
                "CREATE TABLE IF NOT EXISTS room_actions ("
                "id INT AUTO_INCREMENT PRIMARY KEY,"
                "room_code VARCHAR(6) NULL,"
                "username VARCHAR(50) NOT NULL,"
                "room_name VARCHAR(100) NOT NULL,"
                "action_type ENUM('kick', 'ban') NOT NULL,"
                "ban_until DATETIME NULL,"
                "reason TEXT NULL,"
                "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
                ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
            )

            if not column_exists(cursor, 'room_actions', 'room_code'):
                cursor.execute("ALTER TABLE room_actions ADD COLUMN room_code VARCHAR(6) NULL AFTER id")

        connection.commit()
        print('Migration completed successfully.')
    finally:
        connection.close()


if __name__ == '__main__':
    main()
