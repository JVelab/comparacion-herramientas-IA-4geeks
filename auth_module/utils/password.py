import re
from typing import Tuple


PASSWORD_MIN_LENGTH = 8
PASSWORD_REQUIRE_UPPERCASE = True
PASSWORD_REQUIRE_DIGIT = True
PASSWORD_REQUIRE_SPECIAL = True

SPECIAL_CHARS = "!@#$%^&*()_+-=[]{}|;:,.<>?"


def validate_password(password: str) -> Tuple[bool, str]:
    if not password:
        return False, "Password is required"

    if len(password) < PASSWORD_MIN_LENGTH:
        return False, f"Password must be at least {PASSWORD_MIN_LENGTH} characters"

    if PASSWORD_REQUIRE_UPPERCASE and not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"

    if PASSWORD_REQUIRE_DIGIT and not re.search(r"\d", password):
        return False, "Password must contain at least one number"

    if PASSWORD_REQUIRE_SPECIAL and not any(c in SPECIAL_CHARS for c in password):
        return False, "Password must contain at least one special character (!@#$%^&*()_+-=[])"

    return True, ""


def hash_password(password: str) -> str:
    from werkzeug.security import generate_password_hash
    return generate_password_hash(password, method="pbkdf2:sha256")


def verify_password(password: str, password_hash: str) -> bool:
    from werkzeug.security import check_password_hash
    return check_password_hash(password_hash, password)