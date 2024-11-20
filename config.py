import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'a-default-key')  # Use default if SECRET_KEY is not set
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'  # Local SQLite for development


class ProductionConfig(Config):
    # Ensure DATABASE_URL is properly set, or raise an error
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

    # Optional: Add debug logging for missing DATABASE_URL in production
    if not SQLALCHEMY_DATABASE_URI:
        raise RuntimeError("DATABASE_URL is not set in the environment for production.")


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': DevelopmentConfig,
    'default': DevelopmentConfig
}
