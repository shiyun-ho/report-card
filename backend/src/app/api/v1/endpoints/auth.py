from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import UserRole
from app.services import AuthService

router = APIRouter()


# Pydantic schemas for request/response
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    role: UserRole
    school_id: int
    school_name: str

    class Config:
        from_attributes = True

    @classmethod
    def from_user(cls, user):
        """Create UserResponse from User model with school name."""
        return cls(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            role=user.role,
            school_id=user.school_id,
            school_name=user.school.name,
        )


class LoginResponse(BaseModel):
    user: UserResponse
    message: str = "Login successful"


class SessionStatusResponse(BaseModel):
    authenticated: bool
    user: Optional[UserResponse] = None


class LogoutResponse(BaseModel):
    message: str = "Logout successful"


class MessageResponse(BaseModel):
    message: str


# Cookie settings for security
COOKIE_SETTINGS = {
    "httponly": True,
    "secure": False,  # Set to False in development if not using HTTPS
    "samesite": "lax",
    "max_age": 30 * 60,  # 30 minutes in seconds
}


@router.post("/login", response_model=LoginResponse)
async def login(
    login_request: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    """
    Authenticate user and create session.

    Sets secure cookies for session management.
    """
    auth_service = AuthService(db)

    # Authenticate user
    user = auth_service.authenticate_user(
        email=login_request.email, password=login_request.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Get client info for security tracking
    user_agent = request.headers.get("user-agent")
    # Get real IP (considering reverse proxy headers)
    ip_address = (
        request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        or request.headers.get("x-real-ip")
        or request.client.host
    )

    # Create session
    session = auth_service.create_session(
        user=user,
        user_agent=user_agent,
        ip_address=ip_address,
    )

    # Set secure cookies
    response.set_cookie(key="session_id", value=session.id, **COOKIE_SETTINGS)
    response.set_cookie(key="csrf_token", value=session.csrf_token, **COOKIE_SETTINGS)

    return LoginResponse(user=UserResponse.from_user(user))


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    """
    Log out user and destroy session.

    Clears session cookies.
    """
    session_id = request.cookies.get("session_id")

    if session_id:
        auth_service = AuthService(db)
        auth_service.delete_session(session_id)

    # Clear cookies
    response.delete_cookie("session_id", path="/")
    response.delete_cookie("csrf_token", path="/")

    return LogoutResponse()


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Get current authenticated user information.

    Requires valid session cookie.
    """
    session_id = request.cookies.get("session_id")

    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    auth_service = AuthService(db)
    session_data = auth_service.get_session_with_user(session_id)

    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        )

    session, user = session_data

    # Extend session on activity
    auth_service.extend_session(session_id)

    return UserResponse.from_user(user)


@router.get("/status", response_model=SessionStatusResponse)
async def session_status(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Check authentication status.

    Returns user info if authenticated, null if not.
    """
    session_id = request.cookies.get("session_id")

    if not session_id:
        return SessionStatusResponse(authenticated=False)

    auth_service = AuthService(db)
    session_data = auth_service.get_session_with_user(session_id)

    if not session_data:
        return SessionStatusResponse(authenticated=False)

    session, user = session_data

    return SessionStatusResponse(authenticated=True, user=UserResponse.from_user(user))


@router.post("/cleanup-sessions", response_model=MessageResponse)
async def cleanup_expired_sessions(
    db: Session = Depends(get_db),
):
    """
    Admin endpoint to clean up expired sessions.

    Should be called periodically by a background task.
    """
    auth_service = AuthService(db)
    deleted_count = auth_service.cleanup_expired_sessions()

    return MessageResponse(message=f"Cleaned up {deleted_count} expired sessions")


@router.post("/logout-all", response_model=MessageResponse)
async def logout_all_sessions(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    """
    Log out from all sessions for the current user.

    Useful for security purposes (password change, etc.).
    """
    session_id = request.cookies.get("session_id")

    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    auth_service = AuthService(db)
    session_data = auth_service.get_session_with_user(session_id)

    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        )

    session, user = session_data

    # Delete all sessions for this user
    deleted_count = auth_service.delete_user_sessions(user.id)

    # Clear cookies
    response.delete_cookie("session_id", path="/")
    response.delete_cookie("csrf_token", path="/")

    return MessageResponse(message=f"Logged out from {deleted_count} sessions")
