import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret-key-for-dev'
    
    # Database Configuration
    DB_USER = os.environ.get('DB_USER') or 'root'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or '@Password1'
    DB_HOST = os.environ.get('DB_HOST') or 'localhost'
    DB_NAME = os.environ.get('DB_NAME') or 'study_group_db'
    DB_PORT = int(os.environ.get('DB_PORT') or 3306)
    
