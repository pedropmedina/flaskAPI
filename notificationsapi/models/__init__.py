from .base import db, ma


def init_app(app):
    db.init_app(app)
    ma.init_app(app)
    return db
