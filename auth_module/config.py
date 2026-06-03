import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-dev-secret-key-change-in-production")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///auth.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_EMAIL_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_COOKIE_SECURE = os.getenv("JWT_COOKIE_SECURE", "False").lower() == "true"
    JWT_COOKIE_SAMESITE = "Strict"
    JWT_COOKIE_HTTPONLY = True
    JWT_COOKIE_PATH = "/auth/refresh"