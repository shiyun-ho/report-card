import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from app.middleware import SessionMiddleware, SessionSecurityMiddleware, CSRFMiddleware
from app.models import User, Session as UserSession
from app.services import AuthService


# Test app for middleware testing
test_app = FastAPI()


@test_app.get("/test")
async def test_endpoint(request: Request):
    """Test endpoint to check middleware behavior."""
    # Handle missing request.state gracefully
    state = getattr(request, "state", None)
    if state is None:
        return {
            "session_id": None,
            "session_valid": False,
            "user_id": None,
        }
    
    return {
        "session_id": getattr(state, "session_id", None),
        "session_valid": getattr(state, "session_valid", False),
        "user_id": getattr(state, "user", {}).id if hasattr(state, "user") and state.user else None,
    }


@test_app.post("/test-csrf")
async def test_csrf_endpoint():
    """Test endpoint for CSRF protection."""
    return {"message": "CSRF protected endpoint accessed"}


@test_app.get("/static/test.css")
async def test_static_endpoint():
    """Test static resource endpoint."""
    return {"content": "/* CSS content */"}


class TestSessionMiddleware:
    """Test cases for SessionMiddleware."""

    @pytest.fixture
    def middleware_app(self, db_session):
        """Create test app with session middleware."""
        from app.core.database import get_db
        
        def override_get_db():
            try:
                yield db_session
            finally:
                pass
        
        app = FastAPI()
        app.dependency_overrides[get_db] = override_get_db
        
        # Add session middleware
        app.add_middleware(SessionMiddleware, cleanup_interval=5)  # Small interval for testing
        
        @app.get("/test")
        async def test_endpoint(request: Request):
            return {
                "session_id": getattr(request.state, "session_id", None),
                "session_valid": getattr(request.state, "session_valid", False),
                "user_id": getattr(request.state, "user", {}).id if hasattr(request.state, "user") and request.state.user else None,
            }
        
        @app.get("/static/test.css")
        async def test_static_endpoint():
            return {"content": "/* CSS content */"}
        
        return app

    def test_middleware_no_session(self, middleware_app: FastAPI):
        """Test middleware behavior with no session."""
        with TestClient(middleware_app) as client:
            response = client.get("/test")
            
            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] is None
            assert data["session_valid"] is False
            assert data["user_id"] is None

    def test_middleware_valid_session(self, middleware_app: FastAPI, test_session: UserSession, test_user: User):
        """Test middleware behavior with valid session."""
        with TestClient(middleware_app) as client:
            client.cookies.set("session_id", test_session.id)
            
            response = client.get("/test")
            
            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == test_session.id
            assert data["session_valid"] is True
            assert data["user_id"] == test_user.id

    def test_middleware_invalid_session(self, middleware_app: FastAPI):
        """Test middleware behavior with invalid session."""
        with TestClient(middleware_app) as client:
            client.cookies.set("session_id", "invalid_session_id")
            
            response = client.get("/test")
            
            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == "invalid_session_id"
            assert data["session_valid"] is False
            assert data["user_id"] is None

    def test_middleware_expired_session(self, middleware_app: FastAPI, expired_session: UserSession):
        """Test middleware behavior with expired session."""
        with TestClient(middleware_app) as client:
            client.cookies.set("session_id", expired_session.id)
            
            response = client.get("/test")
            
            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == expired_session.id
            assert data["session_valid"] is False
            assert data["user_id"] is None

