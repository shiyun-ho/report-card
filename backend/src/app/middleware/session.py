import logging
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.database import SessionLocal
from app.services import AuthService

logger = logging.getLogger(__name__)


class SessionMiddleware(BaseHTTPMiddleware):
    """
    Middleware for handling session management.

    Automatically validates sessions, extends active sessions,
    and cleans up expired sessions periodically.
    """

    def __init__(self, app, cleanup_interval: int = 100):
        """
        Initialize session middleware.

        Args:
            app: FastAPI application instance
            cleanup_interval: Number of requests between expired session cleanups
        """
        super().__init__(app)
        self.cleanup_interval = cleanup_interval
        self.request_count = 0

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and handle session management.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler

        Returns:
            HTTP response
        """
        # Increment request counter for periodic cleanup
        self.request_count += 1

        # Get session ID from cookies
        session_id = request.cookies.get("session_id")

        # Add session info to request state for easy access
        request.state.session_id = session_id
        request.state.user = None
        request.state.session_valid = False

        # Validate session if present
        if session_id:
            await self._validate_and_extend_session(request, session_id)

        # Process the request
        response = await call_next(request)

        # Periodic cleanup of expired sessions
        if self.request_count % self.cleanup_interval == 0:
            await self._cleanup_expired_sessions()

        # Handle session cookie updates if needed
        await self._update_session_cookies(request, response)

        return response

    async def _validate_and_extend_session(self, request: Request, session_id: str):
        """
        Validate session and extend if valid.

        Args:
            request: HTTP request object
            session_id: Session identifier to validate
        """
        try:
            db = SessionLocal()
            try:
                auth_service = AuthService(db)
                session_data = auth_service.get_session_with_user(session_id)

                if session_data:
                    session, user = session_data

                    # Update request state with session info
                    request.state.session_valid = True
                    request.state.user = user
                    request.state.session = session

                    # Extend session for active users
                    # Only extend for non-static resources
                    if not self._is_static_resource(request):
                        auth_service.extend_session(session_id)

                    logger.debug(f"Valid session for user {user.id} ({user.email})")
                else:
                    logger.debug(f"Invalid or expired session: {session_id}")

            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error validating session {session_id}: {e}")

    async def _cleanup_expired_sessions(self):
        """
        Clean up expired sessions from the database.
        """
        try:
            db = SessionLocal()
            try:
                auth_service = AuthService(db)
                deleted_count = auth_service.cleanup_expired_sessions()

                if deleted_count > 0:
                    logger.info(f"Cleaned up {deleted_count} expired sessions")

            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error during session cleanup: {e}")

    async def _update_session_cookies(self, request: Request, response: Response):
        """
        Update session cookies if needed.

        Args:
            request: HTTP request object
            response: HTTP response object
        """
        # If session was invalidated, clear cookies
        if (
            hasattr(request.state, "session_id")
            and request.state.session_id
            and not request.state.session_valid
        ):
            # Clear invalid session cookies
            response.delete_cookie("session_id", path="/")
            response.delete_cookie("csrf_token", path="/")
            logger.debug("Cleared invalid session cookies")

    def _is_static_resource(self, request: Request) -> bool:
        """
        Check if the request is for a static resource.

        Static resources don't need session extension.

        Args:
            request: HTTP request object

        Returns:
            True if request is for static resource
        """
        path = request.url.path

        # Common static resource patterns
        static_patterns = [
            "/static/",
            "/assets/",
            "/favicon.ico",
            "/robots.txt",
            ".css",
            ".js",
            ".ico",
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".svg",
            ".woff",
            ".woff2",
            ".ttf",
            ".eot",
        ]

        return any(pattern in path for pattern in static_patterns)


class SessionSecurityMiddleware(BaseHTTPMiddleware):
    """
    Security-focused session middleware.

    Provides additional security checks and logging for sessions.
    """

    def __init__(
        self, app, enable_ip_validation: bool = True, enable_user_agent_validation: bool = True
    ):
        """
        Initialize session security middleware.

        Args:
            app: FastAPI application instance
            enable_ip_validation: Whether to validate IP addresses
            enable_user_agent_validation: Whether to validate user agents
        """
        super().__init__(app)
        self.enable_ip_validation = enable_ip_validation
        self.enable_user_agent_validation = enable_user_agent_validation

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with security checks.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler

        Returns:
            HTTP response
        """
        # Perform security checks if session is present
        session_id = request.cookies.get("session_id")

        if session_id and hasattr(request.state, "session_valid") and request.state.session_valid:
            await self._perform_security_checks(request)

        # Process the request
        response = await call_next(request)

        return response

    async def _perform_security_checks(self, request: Request):
        """
        Perform security validation on the session.

        Args:
            request: HTTP request object
        """
        if not hasattr(request.state, "session"):
            return

        session = request.state.session
        current_ip = self._get_client_ip(request)
        current_user_agent = request.headers.get("user-agent")

        # IP address validation
        if self.enable_ip_validation and session.ip_address:
            if current_ip != session.ip_address:
                logger.warning(
                    f"IP address mismatch for session {session.id}: "
                    f"stored={session.ip_address}, current={current_ip}"
                )
                # In a production environment, you might want to invalidate the session
                # For now, just log the mismatch

        # User agent validation
        if self.enable_user_agent_validation and session.user_agent:
            if current_user_agent != session.user_agent:
                logger.warning(
                    f"User agent mismatch for session {session.id}: "
                    f"stored={session.user_agent}, current={current_user_agent}"
                )
                # In a production environment, you might want to invalidate the session
                # For now, just log the mismatch

    def _get_client_ip(self, request: Request) -> str:
        """
        Get the real client IP address, accounting for proxy headers.

        Args:
            request: HTTP request object

        Returns:
            Client IP address
        """
        # Check for forwarded headers (reverse proxy)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fallback to direct connection
        return request.client.host if request.client else "unknown"
