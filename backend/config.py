import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
  
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "..", "database.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT
    JWT_SECRET_KEY = (
        os.environ.get("JWT_SECRET_KEY") or "jwt-secret-key-change-in-production"
    )
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour

    # Redis
    REDIS_URL = os.environ.get("REDIS_URL") or "redis://localhost:6379/0"

    # File Uploads
    UPLOAD_FOLDER = os.path.join(basedir, "..", "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "doc", "docx"}

    # Email (for Celery tasks)
    MAIL_SERVER = os.environ.get("MAIL_SERVER") or "smtp.gmail.com"
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 587)
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() in ["true", "on", "1"]
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")

    # Admin user (created on first run)
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL") or "admin@hospital.com"
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD") or "admin123"
    ADMIN_NAME = os.environ.get("ADMIN_NAME") or "System Administrator"


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}

