from .route import bp as category_bp


def register_bp(app):
    app.register_blueprint(category_bp)
