import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from passlib.context import CryptContext

from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    """
    return pwd_context.hash(password)


def generate_session_id() -> str:
    """
    Generate a secure random session ID.
    """
    return secrets.token_urlsafe(32)


def generate_csrf_token() -> str:
    """
    Generate a CSRF token.
    """
    return secrets.token_urlsafe(32)


def create_session_data(user_id: int, user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create session data for a user.
    """
    return {
        "session_id": generate_session_id(),
        "user_id": user_id,
        "user_data": user_data,
        "created_at": datetime.now(timezone.utc),
        "expires_at": datetime.now(timezone.utc)
        + timedelta(minutes=settings.SESSION_EXPIRE_MINUTES),
        "csrf_token": generate_csrf_token(),
    }


def is_session_expired(expires_at: datetime) -> bool:
    """
    Check if a session has expired.
    """
    return datetime.now(timezone.utc) > expires_at
