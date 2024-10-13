import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or 'a-default-key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@hostname:port/dbname'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': DevelopmentConfig,
    'default': DevelopmentConfig
}