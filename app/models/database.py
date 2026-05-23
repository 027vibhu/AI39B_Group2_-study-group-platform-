import pymysql
from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE


def get_connection():
    """Return a new pymysql connection using settings from config."""
    return pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        cursorclass=pymysql.cursors.DictCursor,
    )


def init_db():
    """Create the `users` table if it doesn't exist."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100) NOT NULL,
                    email VARCHAR(150) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        conn.commit()
    finally:
        conn.close()
