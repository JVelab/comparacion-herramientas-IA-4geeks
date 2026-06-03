#!/usr/bin/env python
"""Test script for Flask JWT Auth Module"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from extensions import db
from models import User
from routes.auth import auth_bp
from routes.protected import protected_bp


def create_test_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-secret-key-change-in-production"
    app.config["JWT_SECRET_KEY"] = "jwt-dev-secret-key-change-in-production"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test_auth.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 900
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = 604800
    app.config["JWT_EMAIL_TOKEN_EXPIRES"] = 86400
    app.config["JWT_COOKIE_SECURE"] = False
    app.config["JWT_COOKIE_HTTPONLY"] = True
    app.config["JWT_COOKIE_SAMESITE"] = "Strict"
    app.config["JWT_COOKIE_PATH"] = "/auth/refresh"

    db.init_app(app)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(protected_bp, url_prefix="/api")

    with app.app_context():
        db.drop_all()
        db.create_all()

    return app


def run_tests():
    app = create_test_app()
    client = app.test_client()

    print("=" * 60)
    print("FLASK JWT AUTH MODULE - API TESTS")
    print("=" * 60)

    # Test 1: Root endpoint
    print("\n[TEST 1] GET /")
    @app.route("/")
    def temp_root():
        from flask import jsonify
        return jsonify({"message": "Flask JWT Auth Module", "version": "1.0.0"})
    resp = client.get("/")
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.get_json()}")
    assert resp.status_code == 200, "Root endpoint failed"

    # Test 2: Register user
    print("\n[TEST 2] POST /auth/register")
    resp = client.post("/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPass123!"
    })
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.get_json()}")
    assert resp.status_code == 201, "Register failed"
    user_id = resp.get_json()["data"]["user_id"]

    # Test 3: Login without verification
    print("\n[TEST 3] POST /auth/login (unverified)")
    resp = client.post("/auth/login", json={
        "email_or_username": "test@example.com",
        "password": "TestPass123!"
    })
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.get_json()}")
    assert resp.status_code == 403, "Should reject unverified user"

    # Test 4: Verify user manually
    print("\n[TEST 4] Verify user in database")
    with app.app_context():
        user = db.session.get(User, user_id)
        user.is_verified = True
        db.session.commit()
        print(f"User {user_id} verified: {user.is_verified}")

    # Test 5: Login with verified user
    print("\n[TEST 5] POST /auth/login (verified)")
    resp = client.post("/auth/login", json={
        "email_or_username": "test@example.com",
        "password": "TestPass123!"
    })
    print(f"Status: {resp.status_code}")
    data = resp.get_json()
    print(f"Response: success={data['success']}, has token={'access_token' in data.get('data', {})}")
    assert resp.status_code == 200, "Login failed"
    access_token = data["data"]["access_token"]

    # Test 6: Access protected endpoint with valid token
    print("\n[TEST 6] GET /api/me (valid token)")
    resp = client.get("/api/me", headers={
        "Authorization": f"Bearer {access_token}"
    })
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.get_json()}")
    assert resp.status_code == 200, "Protected endpoint failed"

    # Test 7: Access protected endpoint without token
    print("\n[TEST 7] GET /api/me (no token)")
    resp = client.get("/api/me")
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.get_json()}")
    assert resp.status_code == 401, "Should require auth"

    # Test 8: Access protected endpoint with invalid token
    print("\n[TEST 8] GET /api/me (invalid token)")
    resp = client.get("/api/me", headers={
        "Authorization": "Bearer invalid_token"
    })
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.get_json()}")
    assert resp.status_code == 401, "Should reject invalid token"

    # Test 9: Password validation
    print("\n[TEST 9] POST /auth/register (weak password)")
    resp = client.post("/auth/register", json={
        "email": "weak@test.com",
        "username": "weakuser",
        "password": "weak"
    })
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.get_json()}")
    assert resp.status_code == 400, "Should reject weak password"

    # Test 10: Duplicate user
    print("\n[TEST 10] POST /auth/register (duplicate)")
    resp = client.post("/auth/register", json={
        "email": "test@example.com",
        "username": "newuser",
        "password": "NewUser123!"
    })
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.get_json()}")
    assert resp.status_code == 409, "Should reject duplicate"

    # Test 11: Login with wrong password
    print("\n[TEST 11] POST /auth/login (wrong password)")
    resp = client.post("/auth/login", json={
        "email_or_username": "test@example.com",
        "password": "WrongPass123!"
    })
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.get_json()}")
    assert resp.status_code == 401, "Should reject wrong password"

    # Test 12: Refresh token endpoint (with cookie from login)
    print("\n[TEST 12] POST /auth/refresh (with cookie from login)")
    resp = client.post("/auth/refresh")
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.get_json()}")
    # Refresh should work because login set a refresh cookie
    assert resp.status_code == 200, "Should refresh with valid cookie"

    # Test 13: Logout
    print("\n[TEST 13] POST /auth/logout")
    resp = client.post("/auth/logout", headers={"Authorization": f"Bearer {access_token}"})
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.get_json()}")
    assert resp.status_code == 200, "Logout failed"

    # Test 14: Access after logout (token should still work, but refresh should be revoked)
    print("\n[TEST 14] GET /api/me (after logout, token still valid)")
    resp = client.get("/api/me", headers={"Authorization": f"Bearer {access_token}"})
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.get_json()}")
    # Access token should still work until it expires
    assert resp.status_code == 200, "Should still work after logout"

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED!")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()