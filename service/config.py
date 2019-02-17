import os

basedir = os.path.abspath(os.path.dirname(__file__))

DB_USER = 'postgress'
DB_PASS = 'pass091313'
DB_ADDR = '127.0.0.1'
DB_NAME = 'flask_notifications'

SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_DATABASE_URI = f'postgress://{DB_USER}:{DB_PASS}@{DB_ADDR}/{DB_NAME}'
