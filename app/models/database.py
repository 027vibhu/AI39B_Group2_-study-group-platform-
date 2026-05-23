import pymysql

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='username',
        password='password',
        database='lorevia_db',
        cursorclass=pymysql.cursors.DictCursor
    )

def init_db():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    id INT PRIMARY KEY,
                    first_name VARCHAR(50) NOT NULL,
                    last_name VARCHAR(50) NOT NULL,
                    bio TEXT,
                    school VARCHAR(100),
                    address VARCHAR(200),
                    profile_picture_url VARCHAR(500)
                )
            """)
        connection.commit()
    finally:
        connection.close()