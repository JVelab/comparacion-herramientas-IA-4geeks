import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any


def _parse_expiry(value):
    from datetime import timedelta
    if isinstance(value, timedelta):
        return value
    return timedelta(seconds=value)


def create_access_token(user_id: int, additional_claims: Optional[Dict[str, Any]] = None) -> str:
    from flask import current_app

    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + _parse_expiry(current_app.config["JWT_ACCESS_TOKEN_EXPIRES"])
    }

    if additional_claims:
        payload.update(additional_claims)

    return jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256")


def create_refresh_token(user_id: int) -> str:
    from flask import current_app

    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + _parse_expiry(current_app.config["JWT_REFRESH_TOKEN_EXPIRES"])
    }

    return jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256")


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    from flask import current_app

    try:
        payload = jwt.decode(
            token,
            current_app.config["JWT_SECRET_KEY"],
            algorithms=["HS256"],
            options={"verify_signature": True, "verify_exp": True}
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    except Exception:
        return None


def get_token_expiry(token: str) -> Optional[datetime]:
    payload = decode_token(token)
    if not payload:
        return None

    exp = payload.get("exp")
    if exp:
        return datetime.fromtimestamp(exp, tz=timezone.utc)
    return None


def hash_token(token: str) -> str:
    import hashlib
    return hashlib.sha256(token.encode()).hexdigest()