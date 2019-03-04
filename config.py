import os


class Config:
    TESTING = False
    DEBUG = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    DB_USERNAME = os.getenv('DB_USERNAME')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_HOST = os.getenv('DB_HOST')
    DB_NAME = os.getenv('DB_NAME')
    DB_URI = 'postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
    SQLALCHEMY_DATABASE_URI = DB_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PAGINATION_PAGE_SIZE = os.getenv('PAGINATION_PAGE_SIZE')
    PAGINATION_PAGE_ARGUMENT_NAME = os.getenv('PAGINATION_PAGE_ARGUMENT_NAME')
    WTF_CSRF_ENABLED = True


class DevConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class ProdCofing(Config):
    DEBUG = False


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SERVER_NAME = '127.0.0.1'
    DB_NAME = os.getenv('TEST_DB_NAME')
