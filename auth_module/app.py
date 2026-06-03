from flask import Flask, jsonify
from auth_module import init_auth_module


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "dev-secret-key-change-in-production"
    app.config["JWT_SECRET_KEY"] = "jwt-dev-secret-key-change-in-production"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///auth.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 900
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = 604800
    app.config["JWT_EMAIL_TOKEN_EXPIRES"] = 86400
    app.config["JWT_COOKIE_SECURE"] = False
    app.config["JWT_COOKIE_HTTPONLY"] = True
    app.config["JWT_COOKIE_SAMESITE"] = "Strict"
    app.config["JWT_COOKIE_PATH"] = "/auth/refresh"

    init_auth_module(app)

    @app.route("/")
    def index():
        return jsonify({
            "message": "Flask JWT Auth Module",
            "version": "1.0.0",
            "endpoints": {
                "auth": {
                    "register": "POST /auth/register",
                    "verify_email": "POST /auth/verify-email",
                    "login": "POST /auth/login",
                    "refresh": "POST /auth/refresh",
                    "logout": "POST /auth/logout",
                    "resend_verification": "POST /auth/resend-verification"
                },
                "protected": {
                    "me": "GET /api/me",
                    "protected": "GET /api/protected"
                }
            }
        })

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)