import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file so DB credentials are picked up correctly

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret-key-for-dev'
    
    # Database Configuration
    DB_USER = os.environ.get('DB_USER') or 'root'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or 'admin123'
    DB_HOST = os.environ.get('DB_HOST') or 'localhost'
    DB_NAME = os.environ.get('DB_NAME') or 'study_group_db'
    DB_PORT = int(os.environ.get('DB_PORT') or 3306)

    # Resend (password reset emails)
    RESEND_API_KEY = os.environ.get('RESEND_API_KEY') or ''
    RESEND_FROM = os.environ.get('RESEND_FROM') or ''

    # The single platform owner/admin. This account is created automatically
    # on startup and is the only user allowed into the admin panel.
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME') or 'admin'
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'admin@lorevia.local'
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'mingmasherpa'

