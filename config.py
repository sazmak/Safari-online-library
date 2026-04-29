import os

def _db_url() -> str:
    url = os.environ.get("DATABASE_URL") or "sqlite:///site.db"
    # SQLAlchemy 2.x requires postgresql:// not postgres://
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dark-academia-secret-777'
    SQLALCHEMY_DATABASE_URI = _db_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024
    ALLOWED_AVATAR_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
    LANGUAGES = ['ru', 'en', 'kk']
    BABEL_DEFAULT_LOCALE = 'ru'
    BABEL_TRANSLATION_DIRECTORIES = 'translations'