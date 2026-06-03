import jwt
import base64
import json
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any


def _parse_expiry(value):
    from datetime import timedelta
    if isinstance(value, timedelta):
        return value
    return timedelta(seconds=value)


def generate_email_token(user_id: int, email: str) -> str:
    from flask import current_app

    payload = {
        "sub": str(user_id),
        "email": email,
        "type": "email_verification",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + _parse_expiry(current_app.config["JWT_EMAIL_TOKEN_EXPIRES"])
    }

    token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")

    return base64.urlsafe_b64encode(token.encode()).decode()


def verify_email_token(token: str) -> Optional[Dict[str, Any]]:
    from flask import current_app

    try:
        decoded = base64.urlsafe_b64decode(token.encode()).decode()
        payload = jwt.decode(
            decoded,
            current_app.config["SECRET_KEY"],
            algorithms=["HS256"]
        )

        if payload.get("type") != "email_verification":
            return None

        return payload
    except Exception:
        return None