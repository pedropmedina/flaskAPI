from .category import bp as category_bp
from .notification import bp as notification_bp
from .user import bp as user_bp


def register_blueprint(app):
    app.register_blueprint(category_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(user_bp)
