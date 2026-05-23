import pymysql
import os

# Try to get database settings from Config if possible, otherwise use defaults
try:
    from config import Config
    # Simple parser for mysql+pymysql://root:password@localhost/study_group_db
    uri = Config.SQLALCHEMY_DATABASE_URI
    if uri.startswith('mysql+pymysql://'):
        rest = uri[len('mysql+pymysql://'):]
        user_pass, host_db = rest.split('@')
        user, password = user_pass.split(':')
        host, db_name = host_db.split('/')
        
        DATABASE_SETTINGS = {
            'host': host,
            'user': user,
            'password': password,
            'database_name': db_name,
            'port': 3306
        }
    else:
        raise ValueError("Invalid URI format")
except Exception:
    DATABASE_SETTINGS = {
        'host': 'localhost',
        'user': 'root',
        'password': 'password',
        'database_name': 'study_group_db',
        'port': 3306
    }

def get_database_settings():
    return DATABASE_SETTINGS

def get_db_connection():
    settings = get_database_settings()
    return pymysql.connect(
        host=settings['host'],
        user=settings['user'],
        password=settings['password'],
        database=settings['database_name'],
        cursorclass=pymysql.cursors.DictCursor
    )

def create_database(
    host: str = "localhost",
    user: str = "root",
    password: str = "",
    database_name: str = "study_group_platform",
    port: int = 3306,
) -> None:
    """Create the database if it does not already exist."""
    connection = pymysql.connect(
        host=host,
        user=user,
        password=password,
        port=port,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{database_name}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
    finally:
        connection.close()

def create_tables(
    host: str = "localhost",
    user: str = "root",
    password: str = "",
    database_name: str = "study_group_platform",
    port: int = 3306,
) -> None:
    """Create required tables in the database."""
    connection = pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database_name,
        port=port,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )

    try:
        with connection.cursor() as cursor:
            # Table from Ritik's branch
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS study_rooms ("
                "id BIGINT AUTO_INCREMENT PRIMARY KEY,"
                "room_name VARCHAR(255) NOT NULL,"
                "room_code VARCHAR(20) NOT NULL UNIQUE,"
                "created_by BIGINT NOT NULL,"
                "is_active BOOLEAN NOT NULL DEFAULT TRUE,"
                "created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"
                ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
            )
            
            # Table from Urbi's branch
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    first_name VARCHAR(50) NOT NULL,
                    last_name VARCHAR(50) NOT NULL,
                    bio TEXT,
                    school VARCHAR(100),
                    address VARCHAR(200),
                    profile_picture_url VARCHAR(500)
                )
            """)
    finally:
        connection.close()

def setup_database() -> None:
    """Create the database and required schema."""
    settings = get_database_settings()
    create_database(**settings)
    create_tables(**settings)

def init_db():
    """Wrapper to match Urbi's naming convention if needed."""
    setup_database()

if __name__ == "__main__":
    setup_database()
    settings = get_database_settings()
    print(f"Database '{settings['database_name']}' and tables are ready.")
