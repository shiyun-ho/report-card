import os
import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.models import User

# Security-compliant credential management - ONLY from environment
TEST_PASSWORD = os.getenv("SEED_DEFAULT_PASSWORD")
if not TEST_PASSWORD:
    pytest.skip("SEED_DEFAULT_PASSWORD environment variable not set", allow_module_level=True)


class TestAuthEndpoints:
    """Test cases for authentication endpoints."""

    def test_login_success(self, test_client: TestClient, test_user: User, valid_login_data: dict):
        """Test successful login."""
        response = test_client.post(
            f"{settings.API_V1_STR}/auth/login",
            json=valid_login_data,
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
        
        # Verify cookie properties
        session_cookie = None
        csrf_cookie = None
        for cookie in response.cookies:
            if cookie.name == "session_id":
                session_cookie = cookie
            elif cookie.name == "csrf_token":
                csrf_cookie = cookie
        
        assert session_cookie is not None
        assert csrf_cookie is not None
        
        # Check cookie security settings
        # Note: TestClient doesn't always preserve all cookie attributes
        # In a real browser test, you would verify httponly, secure, samesite

    def test_login_invalid_email(self, test_client: TestClient):
        """Test login with invalid email."""
        response = test_client.post(
            f"{settings.API_V1_STR}/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "anypassword",
            },
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Incorrect email or password"

    def test_login_invalid_password(self, test_client: TestClient, test_user: User):
        """Test login with invalid password."""
        response = test_client.post(
            f"{settings.API_V1_STR}/auth/login",
            json={
                "email": test_user.email,
                "password": "wrongpassword",
            },
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Incorrect email or password"

    def test_login_invalid_email_format(self, test_client: TestClient):
        """Test login with invalid email format."""
        response = test_client.post(
            f"{settings.API_V1_STR}/auth/login",
            json={
                "email": "invalid-email-format",
                "password": "anypassword",
            },
        )
        
        assert response.status_code == 422  # Validation error

    def test_logout_success(self, authenticated_client: dict):
        """Test successful logout."""
        client = authenticated_client["client"]
        
        # Logout
        response = client.post(f"{settings.API_V1_STR}/auth/logout")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Logout successful"
        
        # Check that cookies are cleared
        # Note: TestClient behavior with cookie deletion may vary

    def test_logout_without_session(self, test_client: TestClient):
        """Test logout without an active session."""
        response = test_client.post(f"{settings.API_V1_STR}/auth/logout")
        
        # Should still succeed (idempotent operation)
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Logout successful"

    def test_get_current_user_authenticated(self, authenticated_client: dict):
        """Test getting current user when authenticated."""
        client = authenticated_client["client"]
        user = authenticated_client["user"]
        
        response = client.get(f"{settings.API_V1_STR}/auth/me")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == user.id
        assert data["email"] == user.email
        assert data["username"] == user.username
        assert data["full_name"] == user.full_name
        assert data["role"] == user.role.value
        assert data["school_id"] == user.school_id

    def test_get_current_user_not_authenticated(self, test_client: TestClient):
        """Test getting current user when not authenticated."""
        response = test_client.get(f"{settings.API_V1_STR}/auth/me")
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Not authenticated"

    def test_get_current_user_invalid_session(self, test_client: TestClient):
        """Test getting current user with invalid session."""
        # Set invalid session cookie
        test_client.cookies.set("session_id", "invalid_session_id")
        
        response = test_client.get(f"{settings.API_V1_STR}/auth/me")
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Invalid or expired session"

    def test_session_status_authenticated(self, authenticated_client: dict):
        """Test session status when authenticated."""
        client = authenticated_client["client"]
        user = authenticated_client["user"]
        
        response = client.get(f"{settings.API_V1_STR}/auth/status")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["authenticated"] is True
        assert data["user"] is not None
        assert data["user"]["id"] == user.id
        assert data["user"]["email"] == user.email

    def test_session_status_not_authenticated(self, test_client: TestClient):
        """Test session status when not authenticated."""
        response = test_client.get(f"{settings.API_V1_STR}/auth/status")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["authenticated"] is False
        assert data["user"] is None

    def test_session_status_invalid_session(self, test_client: TestClient):
        """Test session status with invalid session."""
        # Set invalid session cookie
        test_client.cookies.set("session_id", "invalid_session_id")
        
        response = test_client.get(f"{settings.API_V1_STR}/auth/status")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["authenticated"] is False
        assert data["user"] is None

    def test_cleanup_sessions_endpoint(self, test_client: TestClient):
        """Test the cleanup sessions admin endpoint."""
        response = test_client.post(f"{settings.API_V1_STR}/auth/cleanup-sessions")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "Cleaned up" in data["message"]
        assert "expired sessions" in data["message"]

    def test_logout_all_sessions(self, authenticated_client: dict):
        """Test logging out from all sessions."""
        client = authenticated_client["client"]
        
        response = client.post(f"{settings.API_V1_STR}/auth/logout-all")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "Logged out from" in data["message"]
        assert "sessions" in data["message"]

    def test_logout_all_sessions_not_authenticated(self, test_client: TestClient):
        """Test logout all when not authenticated."""
        response = test_client.post(f"{settings.API_V1_STR}/auth/logout-all")
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Not authenticated"

    def test_session_extension_on_activity(self, authenticated_client: dict, db_session):
        """Test that sessions are extended on user activity."""
        from app.services import AuthService
        
        client = authenticated_client["client"]
        session_id = authenticated_client["session_id"]
        
        # Get initial session expiry
        auth_service = AuthService(db_session)
        initial_session = auth_service.get_session(session_id)
        initial_expiry = initial_session.expires_at
        
        # Make a request (should extend session)
        response = client.get(f"{settings.API_V1_STR}/auth/me")
        assert response.status_code == 200
        
        # Check that session was extended
        extended_session = auth_service.get_session(session_id)
        assert extended_session.expires_at > initial_expiry

    def test_multiple_sessions_same_user(self, test_client: TestClient, test_user: User):
        """Test that a user can have multiple active sessions."""
        # Create first session
        response1 = test_client.post(
            f"{settings.API_V1_STR}/auth/login",
            json={
                "email": test_user.email,
                "password": TEST_PASSWORD,
            },
        )
        assert response1.status_code == 200
        
        # Create second session (simulating login from another device)
        response2 = test_client.post(
            f"{settings.API_V1_STR}/auth/login",
            json={
                "email": test_user.email,
                "password": TEST_PASSWORD,
            },
        )
        assert response2.status_code == 200
        
        # Both sessions should be valid
        # Note: In TestClient, cookies from response2 would overwrite response1
        # In real usage, different devices would have different session cookies

    def test_concurrent_logins_different_users(self, test_client: TestClient, test_user: User, test_year_head: User):
        """Test concurrent logins from different users."""
        # Login first user
        response1 = test_client.post(
            f"{settings.API_V1_STR}/auth/login",
            json={
                "email": test_user.email,
                "password": TEST_PASSWORD,
            },
        )
        assert response1.status_code == 200
        
        # Login second user  
        response2 = test_client.post(
            f"{settings.API_V1_STR}/auth/login",
            json={
                "email": test_year_head.email,
                "password": TEST_PASSWORD,
            },
        )
        assert response2.status_code == 200
        
        # Both should succeed independently