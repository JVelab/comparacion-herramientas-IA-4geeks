from flask import Flask
from extensions import db


def create_auth_blueprint():
    from routes.auth import auth_bp
    from routes.protected import protected_bp
    return auth_bp, protected_bp


def init_auth_module(app: Flask):
    db.init_app(app)

    auth_bp, protected_bp = create_auth_blueprint()
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(protected_bp, url_prefix="/api")

    with app.app_context():
        db.create_all()

    return app