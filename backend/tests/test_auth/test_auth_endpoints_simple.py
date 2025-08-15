"""
Simple authentication endpoint tests without middleware interference.

These tests verify the core authentication functionality works correctly
by testing the endpoints directly without going through the full middleware stack.
"""

import os
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints.auth import router as auth_router
from app.core.config import settings
from app.core.database import get_db
from app.models import User

# Security-compliant credential management - ONLY from environment
TEST_PASSWORD = os.getenv("SEED_DEFAULT_PASSWORD")
if not TEST_PASSWORD:
    pytest.skip("SEED_DEFAULT_PASSWORD environment variable not set", allow_module_level=True)


# Create a simple test app without middleware
def create_test_app(db_session):
    """Create a test FastAPI app without middleware for simple testing."""
    test_app = FastAPI()
    
    # Override database dependency
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    test_app.dependency_overrides[get_db] = override_get_db
    
    # Include auth router
    test_app.include_router(auth_router, prefix="/auth")
    
    return test_app


class TestAuthEndpointsSimple:
    """Simple tests for authentication endpoints without middleware."""

    @pytest.fixture
    def simple_client(self, db_session):
        """Create a simple test client without middleware."""
        test_app = create_test_app(db_session)
        
        with TestClient(test_app) as client:
            yield client

    def test_login_success(self, simple_client: TestClient, test_user: User):
        """Test successful login without middleware."""
        response = simple_client.post(
            "/auth/login",
            json={
                "email": test_user.email,
                "password": TEST_PASSWORD,
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "user" in data
        assert "message" in data
        assert data["message"] == "Login successful"
        
        # Check user data
        user_data = data["user"]
        assert user_data["id"] == test_user.id
        assert user_data["email"] == test_user.email
        assert user_data["username"] == test_user.username
        assert user_data["full_name"] == test_user.full_name
        assert user_data["role"] == test_user.role.value
        assert user_data["school_id"] == test_user.school_id
        
        # Check cookies are set
        assert "session_id" in response.cookies
        assert "csrf_token" in response.cookies

    def test_login_invalid_email(self, simple_client: TestClient):
        """Test login with invalid email."""
        response = simple_client.post(
            "/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "anypassword",
            },
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Incorrect email or password"

    def test_login_invalid_password(self, simple_client: TestClient, test_user: User):
        """Test login with invalid password."""
        response = simple_client.post(
            "/auth/login",
            json={
                "email": test_user.email,
                "password": "wrongpassword",
            },
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Incorrect email or password"

    def test_logout_success(self, simple_client: TestClient):
        """Test successful logout."""
        response = simple_client.post("/auth/logout")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Logout successful"

    def test_get_current_user_not_authenticated(self, simple_client: TestClient):
        """Test getting current user when not authenticated."""
        response = simple_client.get("/auth/me")
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Not authenticated"

    def test_session_status_not_authenticated(self, simple_client: TestClient):
        """Test session status when not authenticated."""
        response = simple_client.get("/auth/status")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["authenticated"] is False
        assert data["user"] is None

    def test_login_creates_session(self, simple_client: TestClient, test_user: User, db_session):
        """Test that login creates a session in the database."""
        from app.services import AuthService
        
        # Get initial session count
        auth_service = AuthService(db_session)
        initial_count = len(db_session.query(auth_service.db.query.__model_class__).all()) if hasattr(auth_service.db.query, '__model_class__') else 0
        
        # Login
        response = simple_client.post(
            "/auth/login",
            json={
                "email": test_user.email,
                "password": TEST_PASSWORD,
            },
        )
        
        assert response.status_code == 200
        
        # Check that a session was created
        session_id = None
        for cookie in response.cookies:
            if cookie.name == "session_id":
                session_id = cookie.value
                break
        
        assert session_id is not None
        
        # Verify session exists in database
        session = auth_service.get_session(session_id)
        assert session is not None
        assert session.user_id == test_user.id

    def test_multiple_user_roles(self, simple_client: TestClient, test_user: User, test_year_head: User, test_admin: User):
        """Test login for different user roles."""
        
        # Test form teacher login
        response = simple_client.post(
            "/auth/login",
            json={
                "email": test_user.email,
                "password": TEST_PASSWORD,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["role"] == "form_teacher"
        
        # Test year head login
        response = simple_client.post(
            "/auth/login",
            json={
                "email": test_year_head.email,
                "password": TEST_PASSWORD,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["role"] == "year_head"
        
        # Test admin login
        response = simple_client.post(
            "/auth/login",
            json={
                "email": test_admin.email,
                "password": TEST_PASSWORD,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["role"] == "admin"

    def test_cleanup_sessions_endpoint(self, simple_client: TestClient):
        """Test the cleanup sessions admin endpoint."""
        response = simple_client.post("/auth/cleanup-sessions")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "Cleaned up" in data["message"]
        assert "expired sessions" in data["message"]

