from typing import Optional, Dict, Any, List


def success_response(message: str, data: Optional[Any] = None) -> Dict[str, Any]:
    response = {
        "success": True,
        "message": message
    }

    if data is not None:
        response["data"] = data

    return response


def error_response(message: str, error_code: str, errors: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
    response = {
        "success": False,
        "message": message,
        "error": error_code
    }

    if errors:
        response["errors"] = errors

    return response


class AuthError(Exception):
    def __init__(self, message: str, error_code: str, status_code: int = 401):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code


AUTH_ERROR_CODES = {
    "AUTH_001": "Invalid credentials",
    "AUTH_002": "Email not verified",
    "AUTH_003": "Token expired",
    "AUTH_004": "Invalid token",
    "AUTH_005": "Refresh token revoked",
    "AUTH_006": "User already exists",
    "AUTH_007": "Email verification token invalid",
    "AUTH_008": "User not found",
    "VAL_001": "Validation failed"
}