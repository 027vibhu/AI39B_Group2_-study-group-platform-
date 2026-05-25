import pymysql
from config import Config


def get_database_connection():
    return pymysql.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        port=Config.DB_PORT,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


def ensure_database_exists():
    connection = pymysql.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        port=Config.DB_PORT,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{Config.DB_NAME}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
    finally:
        connection.close()


def create_users_table():
    ensure_database_exists()

    connection = get_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS users ("
                "id INT AUTO_INCREMENT PRIMARY KEY,"
                "username VARCHAR(50) NOT NULL UNIQUE,"
                "email VARCHAR(255) NOT NULL UNIQUE,"
                "password_hash VARCHAR(255) NOT NULL,"
                "avatar_url VARCHAR(255) NOT NULL DEFAULT 'images/default_user_icon.jpg',"
                "first_name VARCHAR(80) NOT NULL DEFAULT '',"
                "last_name VARCHAR(80) NOT NULL DEFAULT '',"
                "school VARCHAR(160) NOT NULL DEFAULT '',"
                "address VARCHAR(255) NOT NULL DEFAULT '',"
                "bio TEXT,"
                "created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"
                ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
            )

            cursor.execute("SHOW COLUMNS FROM users LIKE 'avatar_url'")
            if not cursor.fetchone():
                cursor.execute(
                    "ALTER TABLE users "
                    "ADD COLUMN avatar_url VARCHAR(255) NOT NULL "
                    "DEFAULT 'images/default_user_icon.jpg'"
                )

            cursor.execute("SHOW COLUMNS FROM users LIKE 'first_name'")
            if not cursor.fetchone():
                cursor.execute(
                    "ALTER TABLE users "
                    "ADD COLUMN first_name VARCHAR(80) NOT NULL DEFAULT ''"
                )

            cursor.execute("SHOW COLUMNS FROM users LIKE 'last_name'")
            if not cursor.fetchone():
                cursor.execute(
                    "ALTER TABLE users "
                    "ADD COLUMN last_name VARCHAR(80) NOT NULL DEFAULT ''"
                )

            cursor.execute("SHOW COLUMNS FROM users LIKE 'school'")
            if not cursor.fetchone():
                cursor.execute(
                    "ALTER TABLE users "
                    "ADD COLUMN school VARCHAR(160) NOT NULL DEFAULT ''"
                )

            cursor.execute("SHOW COLUMNS FROM users LIKE 'address'")
            if not cursor.fetchone():
                cursor.execute(
                    "ALTER TABLE users "
                    "ADD COLUMN address VARCHAR(255) NOT NULL DEFAULT ''"
                )

            cursor.execute("SHOW COLUMNS FROM users LIKE 'bio'")
            if not cursor.fetchone():
                cursor.execute(
                    "ALTER TABLE users "
                    "ADD COLUMN bio TEXT"
                )
    finally:
        connection.close()


def get_user_by_identifier(identifier):
    connection = get_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, username, email, password_hash, avatar_url, "
                "first_name, last_name, school, address, bio, created_at "
                "FROM users WHERE username = %s OR email = %s LIMIT 1",
                (identifier, identifier),
            )
            return cursor.fetchone()
    finally:
        connection.close()


def get_user_by_email(email):
    connection = get_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, username, email, password_hash, avatar_url, "
                "first_name, last_name, school, address, bio, created_at "
                "FROM users WHERE email = %s LIMIT 1",
                (email,),
            )
            return cursor.fetchone()
    finally:
        connection.close()


def get_user_by_username(username):
    connection = get_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, username, email, password_hash, avatar_url, "
                "first_name, last_name, school, address, bio, created_at "
                "FROM users WHERE username = %s LIMIT 1",
                (username,),
            )
            return cursor.fetchone()
    finally:
        connection.close()


def get_user_by_id(user_id):
    connection = get_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, username, email, password_hash, avatar_url, "
                "first_name, last_name, school, address, bio, created_at "
                "FROM users WHERE id = %s LIMIT 1",
                (user_id,),
            )
            return cursor.fetchone()
    finally:
        connection.close()


def create_user(username, email, password_hash):
    create_users_table()

    connection = get_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                (username, email, password_hash),
            )
            return cursor.lastrowid
    finally:
        connection.close()


def update_user_avatar(user_id, avatar_url):
    connection = get_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET avatar_url = %s WHERE id = %s",
                (avatar_url, user_id),
            )
            return cursor.rowcount
    finally:
        connection.close()


def update_user_profile(user_id, first_name, last_name, school, address, bio):
    connection = get_database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET first_name = %s, last_name = %s, school = %s, "
                "address = %s, bio = %s WHERE id = %s",
                (first_name, last_name, school, address, bio, user_id),
            )
            return cursor.rowcount
    finally:
        connection.close()
