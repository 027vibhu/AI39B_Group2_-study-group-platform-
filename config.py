import os
from dotenv import load_dotenv

load_dotenv(override=True)  # .env is the source of truth, even over stale inherited env vars

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret-key-for-dev'
    
    # Database Configuration
    DB_USER = os.environ.get('DB_USER') or 'root'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or 'mingmasherpa'
    DB_HOST = os.environ.get('DB_HOST') or 'localhost'
    DB_NAME = os.environ.get('DB_NAME') or 'study_group_db'
    DB_PORT = int(os.environ.get('DB_PORT') or 3306)

    # Resend (password reset emails)
    RESEND_API_KEY = os.environ.get('RESEND_API_KEY') or ''
    RESEND_FROM = os.environ.get('RESEND_FROM') or ''

    # NVIDIA build API (OpenAI-compatible) for flashcard generation
    NVIDIA_API_KEY = os.environ.get('NVIDIA_API_KEY') or ''
    NVIDIA_BASE_URL = os.environ.get('NVIDIA_BASE_URL') or 'https://integrate.api.nvidia.com/v1'
    NVIDIA_MODEL = os.environ.get('NVIDIA_MODEL') or 'nvidia/nemotron-3-nano-omni-30b-a3b-reasoning'

    # The single platform owner/admin. This account is created automatically
    # on startup and is the only user allowed into the admin panel.
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME') or 'admin'
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'admin@lorevia.local'
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'mingmasherpa'

