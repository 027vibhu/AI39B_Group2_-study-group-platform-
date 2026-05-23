import pymysql
from config import get_database_settings


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
    finally:
        connection.close()


def setup_database() -> None:
    """Create the database and required schema."""
    settings = get_database_settings()
    create_database(**settings)
    create_tables(**settings)


if __name__ == "__main__":
    setup_database()
    settings = get_database_settings()
    print(f"Database '{settings['database_name']}' and tables are ready.")