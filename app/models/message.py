from app.models.database import ensure_database_exists, get_database_connection


def create_messages_table():
    ensure_database_exists()

    connection = get_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS message ("
                "id INT AUTO_INCREMENT PRIMARY KEY,"
                "room_id INT NOT NULL,"
                "username VARCHAR(50) NOT NULL,"
                "content TEXT NOT NULL,"
                "timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
                "INDEX idx_message_room (room_id)"
                ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
            )
    finally:
        connection.close()


def create_message(room_id, username, content):
    create_messages_table()

    connection = get_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO message (room_id, username, content) VALUES (%s, %s, %s)",
                (room_id, username, content),
            )
            return cursor.lastrowid
    finally:
        connection.close()


def get_messages_for_room(room_id):
    connection = get_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, room_id, username, content, timestamp "
                "FROM message WHERE room_id = %s ORDER BY timestamp ASC",
                (room_id,),
            )
            rows = cursor.fetchall()
            for row in rows:
                timestamp = row.get('timestamp')
                if timestamp and hasattr(timestamp, 'strftime'):
                    row['time_label'] = timestamp.strftime('%I:%M %p')
                else:
                    row['time_label'] = ''
            return rows
    finally:
        connection.close()
