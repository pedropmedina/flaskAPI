from flask import Flask
from flask_migrate import Migrate


def create_app(config=None):
    from . import db, category, notification

    # instantiate flask app
    app = Flask(__name__)

    # configure app
    if config is None:
        app.config.from_envvar('APP_CONFIG', silent=True)
    else:
        app.config.from_mapping(config)

    # initialize database and blueprints
    db.init_app(app)
    notification.register_bp(app)
    category.register_bp(app)

    Migrate(app, db)

    return app
