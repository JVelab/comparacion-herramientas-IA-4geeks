from functools import wraps
from flask import request, jsonify, g
from utils.jwt_utils import decode_token
from utils.responses import error_response, AuthError, AUTH_ERROR_CODES


def get_token_from_header():
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return None

    parts = auth_header.split()

    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    return parts[1]


def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_header()

        if not token:
            return jsonify(error_response(
                AUTH_ERROR_CODES["AUTH_004"],
                "AUTH_004"
            )), 401

        payload = decode_token(token)

        if not payload:
            return jsonify(error_response(
                AUTH_ERROR_CODES["AUTH_004"],
                "AUTH_004"
            )), 401

        if payload.get("type") != "access":
            return jsonify(error_response(
                AUTH_ERROR_CODES["AUTH_004"],
                "AUTH_004"
            )), 401

        g.user_id = payload.get("sub")

        return f(*args, **kwargs)

    return decorated


def verify_email_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        from models import User
        from extensions import db

        user = db.session.get(User, g.user_id)

        if not user or not user.is_verified:
            return jsonify(error_response(
                AUTH_ERROR_CODES["AUTH_002"],
                "AUTH_002"
            )), 403

        return f(*args, **kwargs)

    return decorated