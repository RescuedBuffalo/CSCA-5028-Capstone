import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'a-default-key')  # Use default if SECRET_KEY is not set
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'  # Local SQLite for development


class ProductionConfig(Config):
    # Ensure SQLALCHEMY_DATABASE_URI is properly set, or raise an error
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': DevelopmentConfig,
    'default': DevelopmentConfig
}
