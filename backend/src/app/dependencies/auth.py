from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User, UserRole
from app.services import AuthService


async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency to get current authenticated user from session.

    Raises HTTP 401 if not authenticated or session is invalid.

    Args:
        request: FastAPI request object containing cookies
        db: Database session

    Returns:
        Authenticated user object

    Raises:
        HTTPException: 401 if not authenticated
    """
    session_id = request.cookies.get("session_id")

    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Session"},
        )

    auth_service = AuthService(db)
    session_data = auth_service.get_session_with_user(session_id)

    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
            headers={"WWW-Authenticate": "Session"},
        )

    session, user = session_data

    # Extend session on activity
    auth_service.extend_session(session_id)

    return user


async def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    Dependency to optionally get current user.

    Returns None if not authenticated, does not raise exceptions.

    Args:
        request: FastAPI request object containing cookies
        db: Database session

    Returns:
        User object if authenticated, None otherwise
    """
    try:
        return await get_current_user(request, db)
    except HTTPException:
        return None


async def require_role(required_role: UserRole):
    """
    Create a dependency that requires a specific user role.

    Args:
        required_role: The role required to access the endpoint

    Returns:
        Dependency function that checks user role
    """

    async def role_dependency(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role.value}",
            )
        return current_user

    return role_dependency


async def require_form_teacher(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency that requires FORM_TEACHER role.

    Args:
        current_user: Current authenticated user

    Returns:
        User object if authorized

    Raises:
        HTTPException: 403 if user is not a form teacher
    """
    if current_user.role != UserRole.FORM_TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Form teacher role required.",
        )
    return current_user


async def require_year_head(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency that requires YEAR_HEAD role.

    Args:
        current_user: Current authenticated user

    Returns:
        User object if authorized

    Raises:
        HTTPException: 403 if user is not a year head
    """
    if current_user.role != UserRole.YEAR_HEAD:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Year head role required.",
        )
    return current_user


async def require_year_head_or_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency that requires YEAR_HEAD or ADMIN role.

    Args:
        current_user: Current authenticated user

    Returns:
        User object if authorized

    Raises:
        HTTPException: 403 if user is not a year head or admin
    """
    if current_user.role not in [UserRole.YEAR_HEAD, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Year head or admin role required.",
        )
    return current_user


async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency that requires ADMIN role.

    Args:
        current_user: Current authenticated user

    Returns:
        User object if authorized

    Raises:
        HTTPException: 403 if user is not an admin
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin role required.",
        )
    return current_user


async def get_current_user_school_id(
    current_user: User = Depends(get_current_user),
) -> int:
    """
    Dependency to get the school_id of the current user.

    Useful for multi-tenant data filtering.

    Args:
        current_user: Current authenticated user

    Returns:
        School ID of the current user
    """
    return current_user.school_id


async def verify_csrf_token(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> bool:
    """
    Dependency to verify CSRF token for state-changing operations.

    Args:
        request: FastAPI request object
        current_user: Current authenticated user
        db: Database session

    Returns:
        True if CSRF token is valid

    Raises:
        HTTPException: 403 if CSRF token is invalid or missing
    """
    # Get CSRF token from cookie
    csrf_token_cookie = request.cookies.get("csrf_token")

    # Get CSRF token from header (for AJAX requests)
    csrf_token_header = request.headers.get("x-csrf-token")

    # Get session ID
    session_id = request.cookies.get("session_id")

    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session required for CSRF validation",
        )

    # Prefer header token over cookie token
    csrf_token = csrf_token_header or csrf_token_cookie

    if not csrf_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token required",
        )

    auth_service = AuthService(db)
    is_valid = auth_service.validate_csrf_token(session_id, csrf_token)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid CSRF token",
        )

    return True


class SchoolIsolationDependency:
    """
    Dependency class for enforcing multi-tenant school isolation.

    Ensures users can only access data from their own school.
    """

    def __init__(self, allow_cross_school_access: bool = False):
        """
        Initialize school isolation dependency.

        Args:
            allow_cross_school_access: If True, admins can access other schools' data
        """
        self.allow_cross_school_access = allow_cross_school_access

    async def __call__(
        self,
        current_user: User = Depends(get_current_user),
    ) -> int:
        """
        Get the school ID that the current user is allowed to access.

        Args:
            current_user: Current authenticated user

        Returns:
            School ID the user can access
        """
        # Admin users might be allowed cross-school access in some contexts
        if self.allow_cross_school_access and current_user.role == UserRole.ADMIN:
            # For admin cross-school access, additional logic would be needed
            # to determine which school they want to access (e.g., from query params)
            pass

        # Return user's own school ID for normal isolation
        return current_user.school_id


# Common dependency instances
require_school_isolation = SchoolIsolationDependency()
require_school_isolation_admin_override = SchoolIsolationDependency(allow_cross_school_access=True)
