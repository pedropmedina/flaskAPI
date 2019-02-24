from .route import bp as notification_bp


def register_bp(app):
    app.register_blueprint(notification_bp)
