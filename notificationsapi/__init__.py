import os
from flask import Flask
from flask_migrate import Migrate


def create_app(config=None):
    from .models import init_app
    from .routes import register_blueprint

    # instantiate flask app
    app = Flask(__name__)

    # configure app
    if config is None:
        app.config.from_object(os.getenv('APP_SETTINGS'))
    else:
        app.config.from_mapping(config)

    # initialize database and blueprints
    db = init_app(app)
    register_blueprint(app)

    Migrate(app, db)

    return app
