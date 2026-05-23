import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret-key-for-dev'
    # Format: mysql+pymysql://username:password@localhost/db_name
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://root:password@localhost/study_group_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
