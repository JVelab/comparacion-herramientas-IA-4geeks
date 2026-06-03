from datetime import datetime, timedelta, timezone

from flask import Blueprint, request, jsonify, g
from sqlalchemy import or_

from models import User, RefreshToken
from extensions import db
from utils import (
    validate_password,
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_token_expiry,
    hash_token,
    generate_email_token,
    verify_email_token,
    success_response,
    error_response,
    AUTH_ERROR_CODES,
    get_email_sender
)


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data:
        return jsonify(error_response("Request body is required", "VAL_001")), 400

    email = data.get("email", "").strip().lower()
    username = data.get("username", "").strip()
    password = data.get("password", "")

    errors = []

    if not email and not username:
        errors.append({"field": "email/username", "message": "Email or username is required"})

    if email and not _is_valid_email(email):
        errors.append({"field": "email", "message": "Invalid email format"})

    if username and not _is_valid_username(username):
        errors.append({"field": "username", "message": "Username must be 3-80 characters (letters, numbers, underscore)"})

    is_valid, password_error = validate_password(password)
    if not is_valid:
        errors.append({"field": "password", "message": password_error})

    if errors:
        return jsonify(error_response("Validation failed", "VAL_001", errors)), 400

    existing_conditions = []
    if email:
        existing_conditions.append(User.email == email)
    if username:
        existing_conditions.append(User.username == username)

    existing_user = User.query.filter(or_(*existing_conditions)).first() if existing_conditions else None

    if existing_user:
        field = "email" if existing_user.email == email else "username"
        return jsonify(error_response("User already exists", "AUTH_006")), 409

    user = User(
        email=email if email else None,
        username=username if username else None,
        password_hash=hash_password(password),
        is_verified=False
    )

    db.session.add(user)
    db.session.commit()

    if email:
        token = generate_email_token(user.id, email)
        email_sender = get_email_sender()
        verification_url = f"http://localhost:5000/auth/verify-email?token={token}"
        email_body = f"Click the link to verify your email: {verification_url}"
        email_sender.send(email, "Verify your email", email_body)

    return jsonify(success_response(
        "User registered successfully. Please check email to verify." if email else "User registered successfully",
        {"user_id": user.id}
    )), 201


@auth_bp.route("/verify-email", methods=["POST"])
def verify_email():
    token = request.args.get("token")

    if not token:
        return jsonify(error_response("Token is required", "VAL_001")), 400

    payload = verify_email_token(token)

    if not payload:
        return jsonify(error_response("Invalid or expired token", "AUTH_007")), 400

    user_id = payload.get("sub")
    token_email = payload.get("email")

    user = db.session.get(User, user_id)

    if not user:
        return jsonify(error_response("User not found", "AUTH_008")), 404

    if user.is_verified:
        return jsonify(success_response("Email already verified", {"is_verified": True})), 200

    if token_email and user.email != token_email:
        return jsonify(error_response("Token does not match user email", "AUTH_007")), 400

    user.is_verified = True
    db.session.commit()

    return jsonify(success_response("Email verified successfully", {"is_verified": True})), 200


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify(error_response("Request body is required", "VAL_001")), 400

    identifier = data.get("email_or_username", "").strip()
    password = data.get("password", "")

    if not identifier or not password:
        return jsonify(error_response("Email/username and password are required", "VAL_001")), 400

    user = User.query.filter(
        (User.email == identifier.lower()) | (User.username == identifier)
    ).first()

    if not user:
        return jsonify(error_response("Invalid credentials", "AUTH_001")), 401

    if not verify_password(password, user.password_hash):
        return jsonify(error_response("Invalid credentials", "AUTH_001")), 401

    if not user.is_verified:
        return jsonify(error_response("Please verify your email first", "AUTH_002")), 403

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    _store_refresh_token(user.id, refresh_token)

    response = jsonify(success_response("Login successful", {
        "access_token": access_token,
        "user": user.to_dict()
    }))

    _set_refresh_cookie(response, refresh_token)

    return response, 200


@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        return jsonify(error_response("Refresh token required", "AUTH_004")), 401

    payload = decode_token(refresh_token)

    if not payload or payload.get("type") != "refresh":
        return jsonify(error_response("Invalid refresh token", "AUTH_004")), 401

    token_hash = hash_token(refresh_token)
    stored_token = RefreshToken.query.filter_by(token_hash=token_hash, is_revoked=False).first()

    if not stored_token:
        return jsonify(error_response("Refresh token revoked or invalid", "AUTH_005")), 401

    if stored_token.expires_at.replace(tzinfo=None) < datetime.utcnow():
        return jsonify(error_response("Refresh token expired", "AUTH_003")), 401

    user = db.session.get(User, stored_token.user_id)

    if not user or not user.is_verified:
        return jsonify(error_response("User not found or not verified", "AUTH_008")), 401

    new_access_token = create_access_token(user.id)

    return jsonify(success_response("Token refreshed", {
        "access_token": new_access_token
    })), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    refresh_token = request.cookies.get("refresh_token")

    if refresh_token:
        token_hash = hash_token(refresh_token)
        stored_token = RefreshToken.query.filter_by(token_hash=token_hash).first()

        if stored_token:
            stored_token.is_revoked = True
            db.session.commit()

    response = jsonify(success_response("Logged out successfully"))
    response.delete_cookie("refresh_token", path="/auth/refresh")

    return response, 200


@auth_bp.route("/resend-verification", methods=["POST"])
def resend_verification():
    data = request.get_json()

    if not data:
        return jsonify(error_response("Request body is required", "VAL_001")), 400

    identifier = data.get("email_or_username", "").strip()

    if not identifier:
        return jsonify(error_response("Email or username is required", "VAL_001")), 400

    user = User.query.filter(
        (User.email == identifier.lower()) | (User.username == identifier)
    ).first()

    if not user:
        return jsonify(success_response("If the user exists, a verification email has been sent")), 200

    if user.is_verified:
        return jsonify(error_response("Email already verified", "AUTH_006")), 409

    if not user.email:
        return jsonify(error_response("No email associated with this account", "VAL_001")), 400

    token = generate_email_token(user.id, user.email)
    email_sender = get_email_sender()
    verification_url = f"http://localhost:5000/auth/verify-email?token={token}"
    email_body = f"Click the link to verify your email: {verification_url}"
    email_sender.send(user.email, "Verify your email", email_body)

    return jsonify(success_response("Verification email sent")), 200


def _is_valid_email(email: str) -> bool:
    import re
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def _is_valid_username(username: str) -> bool:
    import re
    pattern = r"^[a-zA-Z0-9_]{3,80}$"
    return bool(re.match(pattern, username))


def _store_refresh_token(user_id: int, token: str) -> None:
    from datetime import datetime, timedelta, timezone

    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    stored_token = RefreshToken(
        user_id=user_id,
        token_hash=hash_token(token),
        expires_at=expires_at
    )

    db.session.add(stored_token)
    db.session.commit()


def _set_refresh_cookie(response, token: str) -> None:
    from flask import current_app

    response.set_cookie(
        "refresh_token",
        token,
        httponly=current_app.config["JWT_COOKIE_HTTPONLY"],
        secure=current_app.config["JWT_COOKIE_SECURE"],
        samesite=current_app.config["JWT_COOKIE_SAMESITE"],
        path=current_app.config["JWT_COOKIE_PATH"],
        max_age=7 * 24 * 3600
    )