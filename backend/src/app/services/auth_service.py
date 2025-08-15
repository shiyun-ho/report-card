from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.core.security import (
    generate_csrf_token,
    generate_session_id,
    is_session_expired,
    verify_password,
)
from app.models import Session as UserSession
from app.models import User


class AuthService:
    """
    Authentication service for session-based authentication.

    Handles user authentication, session management, and security.
    Implements multi-tenant isolation via school_id.
    """

    def __init__(self, db: Session):
        self.db = db

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user by email and password.

        Args:
            email: User's email address
            password: Plain text password

        Returns:
            User object if authentication successful, None otherwise
        """
        user = self.db.query(User).options(joinedload(User.school)).filter(User.email == email).first()

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user

    def create_session(
        self,
        user: User,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> UserSession:
        """
        Create a new session for a user.

        Args:
            user: Authenticated user
            user_agent: Browser user agent string
            ip_address: Client IP address

        Returns:
            Created session object
        """
        session_id = generate_session_id()
        csrf_token = generate_csrf_token()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.SESSION_EXPIRE_MINUTES)

        session = UserSession(
            id=session_id,
            user_id=user.id,
            expires_at=expires_at,
            csrf_token=csrf_token,
            user_agent=user_agent,
            ip_address=ip_address,
        )

        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        return session

    def get_session(self, session_id: str) -> Optional[UserSession]:
        """
        Get a session by ID if it exists and is valid.

        Args:
            session_id: Session identifier

        Returns:
            Session object if valid, None if not found or expired
        """
        session = self.db.query(UserSession).filter(UserSession.id == session_id).first()

        if not session:
            return None

        # Check if session is expired
        if is_session_expired(session.expires_at):
            # Clean up expired session
            self.delete_session(session_id)
            return None

        return session

    def get_session_with_user(self, session_id: str) -> Optional[tuple[UserSession, User]]:
        """
        Get session with associated user data.

        Args:
            session_id: Session identifier

        Returns:
            Tuple of (session, user) if valid, None otherwise
        """
        session = self.db.query(UserSession).filter(UserSession.id == session_id).first()

        if not session:
            return None

        # Check if session is expired
        if is_session_expired(session.expires_at):
            self.delete_session(session_id)
            return None

        # Get user with session (enforces multi-tenant isolation) and include school
        user = self.db.query(User).options(joinedload(User.school)).filter(User.id == session.user_id).first()

        if not user:
            # Orphaned session, clean it up
            self.delete_session(session_id)
            return None

        return session, user

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session by ID.

        Args:
            session_id: Session identifier to delete

        Returns:
            True if session was deleted, False if not found
        """
        session = self.db.query(UserSession).filter(UserSession.id == session_id).first()

        if session:
            self.db.delete(session)
            self.db.commit()
            return True

        return False

    def delete_user_sessions(self, user_id: int) -> int:
        """
        Delete all sessions for a specific user.

        Args:
            user_id: User ID to delete sessions for

        Returns:
            Number of sessions deleted
        """
        deleted_count = self.db.query(UserSession).filter(UserSession.user_id == user_id).delete()

        self.db.commit()
        return deleted_count

    def cleanup_expired_sessions(self) -> int:
        """
        Remove all expired sessions from the database.

        This should be called periodically to clean up stale sessions.

        Returns:
            Number of expired sessions deleted
        """
        now = datetime.now(timezone.utc)

        deleted_count = self.db.query(UserSession).filter(UserSession.expires_at < now).delete()

        self.db.commit()
        return deleted_count

    def extend_session(self, session_id: str) -> Optional[UserSession]:
        """
        Extend the expiration time of an active session.

        Args:
            session_id: Session identifier to extend

        Returns:
            Updated session if successful, None if session not found or expired
        """
        session = self.get_session(session_id)

        if not session:
            return None

        # Extend expiration
        session.expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.SESSION_EXPIRE_MINUTES
        )

        self.db.commit()
        self.db.refresh(session)

        return session

    def validate_csrf_token(self, session_id: str, csrf_token: str) -> bool:
        """
        Validate CSRF token for a session.

        Args:
            session_id: Session identifier
            csrf_token: CSRF token to validate

        Returns:
            True if CSRF token is valid, False otherwise
        """
        session = self.get_session(session_id)

        if not session:
            return False

        return session.csrf_token == csrf_token
