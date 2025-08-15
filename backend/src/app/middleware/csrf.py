import logging
from typing import Callable, List, Set

from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.database import SessionLocal
from app.services import AuthService

logger = logging.getLogger(__name__)


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    CSRF (Cross-Site Request Forgery) protection middleware.

    Validates CSRF tokens for state-changing HTTP methods.
    Implements the double-submit cookie pattern for security.
    """

    def __init__(
        self,
        app,
        protected_methods: Set[str] = None,
        exempt_paths: List[str] = None,
        require_referer_check: bool = True,
        allowed_hosts: List[str] = None,
    ):
        """
        Initialize CSRF middleware.

        Args:
            app: FastAPI application instance
            protected_methods: HTTP methods that require CSRF protection
            exempt_paths: Paths that are exempt from CSRF protection
            require_referer_check: Whether to validate referer header
            allowed_hosts: List of allowed hosts for referer validation
        """
        super().__init__(app)

        # Default protected methods (state-changing operations)
        self.protected_methods = protected_methods or {"POST", "PUT", "DELETE", "PATCH"}

        # Default exempt paths
        self.exempt_paths = set(
            exempt_paths
            or [
                "/docs",
                "/redoc",
                "/openapi.json",
                "/api/v1/auth/login",  # Login endpoint creates session
                "/api/v1/health",  # Health check
            ]
        )

        self.require_referer_check = require_referer_check
        self.allowed_hosts = set(allowed_hosts or ["localhost", "127.0.0.1"])

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and validate CSRF token if needed.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler

        Returns:
            HTTP response

        Raises:
            HTTPException: 403 if CSRF validation fails
        """
        # Check if this request needs CSRF protection
        if self._requires_csrf_protection(request):
            await self._validate_csrf_token(request)

        # Process the request
        response = await call_next(request)

        return response

    def _requires_csrf_protection(self, request: Request) -> bool:
        """
        Determine if a request requires CSRF protection.

        Args:
            request: HTTP request object

        Returns:
            True if CSRF protection is required
        """
        # Only protect state-changing methods
        if request.method not in self.protected_methods:
            return False

        # Check if path is exempt
        path = request.url.path
        if any(path.startswith(exempt_path) for exempt_path in self.exempt_paths):
            return False

        # Require CSRF protection for authenticated users only
        session_id = request.cookies.get("session_id")
        return bool(session_id)

    async def _validate_csrf_token(self, request: Request):
        """
        Validate CSRF token for the request.

        Args:
            request: HTTP request object

        Raises:
            HTTPException: 403 if CSRF validation fails
        """
        # Get session ID
        session_id = request.cookies.get("session_id")
        if not session_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session required for CSRF protection",
            )

        # Get CSRF token from header (preferred for AJAX requests)
        csrf_token_header = request.headers.get("x-csrf-token")

        # Get CSRF token from form data (for traditional form submissions)
        csrf_token_form = None
        if request.method == "POST" and "application/x-www-form-urlencoded" in request.headers.get(
            "content-type", ""
        ):
            try:
                form_data = await request.form()
                csrf_token_form = form_data.get("csrf_token")
            except Exception:
                pass  # Continue without form token

        # Get CSRF token from cookie (double-submit pattern)
        csrf_token_cookie = request.cookies.get("csrf_token")

        # Prefer header, then form, then cookie
        csrf_token = csrf_token_header or csrf_token_form or csrf_token_cookie

        if not csrf_token:
            logger.warning(f"Missing CSRF token for {request.method} {request.url.path}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token required",
            )

        # Validate token against session
        if not await self._verify_csrf_token(session_id, csrf_token):
            logger.warning(f"Invalid CSRF token for session {session_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid CSRF token",
            )

        # Additional referer check if enabled
        if self.require_referer_check:
            self._validate_referer(request)

        logger.debug(f"CSRF validation passed for {request.method} {request.url.path}")

    async def _verify_csrf_token(self, session_id: str, csrf_token: str) -> bool:
        """
        Verify CSRF token against session data.

        Args:
            session_id: Session identifier
            csrf_token: CSRF token to validate

        Returns:
            True if token is valid
        """
        try:
            db = SessionLocal()
            try:
                auth_service = AuthService(db)
                return auth_service.validate_csrf_token(session_id, csrf_token)
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error validating CSRF token: {e}")
            return False

    def _validate_referer(self, request: Request):
        """
        Validate referer header for additional CSRF protection.

        Args:
            request: HTTP request object

        Raises:
            HTTPException: 403 if referer validation fails
        """
        referer = request.headers.get("referer")

        if not referer:
            logger.warning(f"Missing referer header for {request.method} {request.url.path}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Referer header required",
            )

        # Parse referer URL
        try:
            from urllib.parse import urlparse

            parsed_referer = urlparse(referer)
            referer_host = parsed_referer.hostname

            # Check if referer host is allowed
            if referer_host not in self.allowed_hosts:
                logger.warning(f"Invalid referer host: {referer_host}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid referer",
                )

        except Exception as e:
            logger.warning(f"Error parsing referer {referer}: {e}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid referer format",
            )

    def add_exempt_path(self, path: str):
        """
        Add a path to the CSRF exemption list.

        Args:
            path: Path to exempt from CSRF protection
        """
        self.exempt_paths.add(path)

    def remove_exempt_path(self, path: str):
        """
        Remove a path from the CSRF exemption list.

        Args:
            path: Path to remove from exemption list
        """
        self.exempt_paths.discard(path)

    def add_allowed_host(self, host: str):
        """
        Add a host to the allowed referer hosts.

        Args:
            host: Host to add to allowed list
        """
        self.allowed_hosts.add(host)


class CSRFTokenMiddleware(BaseHTTPMiddleware):
    """
    Middleware for injecting CSRF tokens into responses.

    Adds CSRF token to HTML responses for easy access in forms.
    """

    def __init__(self, app, token_name: str = "csrf_token"):
        """
        Initialize CSRF token middleware.

        Args:
            app: FastAPI application instance
            token_name: Name of the CSRF token variable in templates
        """
        super().__init__(app)
        self.token_name = token_name

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and inject CSRF token into response.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler

        Returns:
            HTTP response with CSRF token injected
        """
        # Get CSRF token from session if available
        csrf_token = None
        session_id = request.cookies.get("session_id")

        if session_id:
            csrf_token = await self._get_csrf_token(session_id)

        # Add CSRF token to request state for templates
        request.state.csrf_token = csrf_token

        # Process the request
        response = await call_next(request)

        # Inject CSRF token into HTML responses
        if csrf_token and self._is_html_response(response):
            await self._inject_csrf_token(response, csrf_token)

        return response

    async def _get_csrf_token(self, session_id: str) -> str | None:
        """
        Get CSRF token for a session.

        Args:
            session_id: Session identifier

        Returns:
            CSRF token if session exists
        """
        try:
            db = SessionLocal()
            try:
                auth_service = AuthService(db)
                session = auth_service.get_session(session_id)
                return session.csrf_token if session else None
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error getting CSRF token: {e}")
            return None

    def _is_html_response(self, response: Response) -> bool:
        """
        Check if response is HTML content.

        Args:
            response: HTTP response object

        Returns:
            True if response contains HTML
        """
        content_type = response.headers.get("content-type", "")
        return "text/html" in content_type

    async def _inject_csrf_token(self, response: Response, csrf_token: str):
        """
        Inject CSRF token into HTML response.

        Args:
            response: HTTP response object
            csrf_token: CSRF token to inject
        """
        # This is a simplified implementation
        # In a real application, you might want to use a proper HTML parser
        # or template engine integration

        if hasattr(response, "body"):
            try:
                body = response.body.decode("utf-8")

                # Inject CSRF token as a meta tag
                csrf_meta = f'<meta name="{self.token_name}" content="{csrf_token}">'

                # Insert after <head> tag if present
                if "<head>" in body:
                    body = body.replace("<head>", f"<head>\n    {csrf_meta}")
                    response.body = body.encode("utf-8")

            except Exception as e:
                logger.error(f"Error injecting CSRF token: {e}")


# Common CSRF middleware configurations
def create_csrf_middleware(app, development_mode: bool = False):
    """
    Create CSRF middleware with appropriate configuration.

    Args:
        app: FastAPI application instance
        development_mode: Whether running in development mode

    Returns:
        Configured CSRF middleware
    """
    allowed_hosts = ["localhost", "127.0.0.1"]

    if not development_mode:
        # Add production hosts
        allowed_hosts.extend(
            [
                # Add your production domain(s) here
                # "your-domain.com",
                # "www.your-domain.com",
            ]
        )

    return CSRFMiddleware(
        app,
        require_referer_check=not development_mode,  # Disable referer check in dev
        allowed_hosts=allowed_hosts,
    )
