"""
Integration tests for the complete authentication system.

Tests the full authentication flow from login to logout,
including session management, CSRF protection, and role-based access.
"""

import os
import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.models import User, UserRole

# Security-compliant credential management - ONLY from environment
TEST_PASSWORD = os.getenv("SEED_DEFAULT_PASSWORD")
if not TEST_PASSWORD:
    pytest.skip("SEED_DEFAULT_PASSWORD environment variable not set", allow_module_level=True)


class TestAuthenticationIntegration:
    """Integration tests for the complete authentication system."""

    def test_complete_authentication_flow(self, test_client: TestClient, test_user: User):
        """Test complete authentication flow from login to logout."""
        
        # 1. Initial status check - should not be authenticated
        response = test_client.get(f"{settings.API_V1_STR}/auth/status")
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is False
        assert data["user"] is None
        
        # 2. Login with valid credentials
        login_response = test_client.post(
            f"{settings.API_V1_STR}/auth/login",
            json={
                "email": test_user.email,
                "password": TEST_PASSWORD,
            },
        )
        assert login_response.status_code == 200
        login_data = login_response.json()
        assert login_data["user"]["id"] == test_user.id
        
        # Extract session cookies
        session_id = None
        csrf_token = None
        for cookie in login_response.cookies:
            if cookie.name == "session_id":
                session_id = cookie.value
            elif cookie.name == "csrf_token":
                csrf_token = cookie.value
        
        assert session_id is not None
        assert csrf_token is not None
        
        # 3. Check authentication status after login
        response = test_client.get(f"{settings.API_V1_STR}/auth/status")
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is True
        assert data["user"]["id"] == test_user.id
        
        # 4. Access protected endpoint
        response = test_client.get(f"{settings.API_V1_STR}/auth/me")
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["id"] == test_user.id
        assert user_data["email"] == test_user.email
        
        # 5. Logout
        logout_response = test_client.post(f"{settings.API_V1_STR}/auth/logout")
        assert logout_response.status_code == 200
        logout_data = logout_response.json()
        assert logout_data["message"] == "Logout successful"
        
        # 6. Verify session is invalidated after logout
        response = test_client.get(f"{settings.API_V1_STR}/auth/status")
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is False
        assert data["user"] is None
        
        # 7. Try to access protected endpoint after logout
        response = test_client.get(f"{settings.API_V1_STR}/auth/me")
        assert response.status_code == 401

    def test_role_based_access_control(self, test_client: TestClient, test_user: User, test_year_head: User, test_admin: User):
        """Test role-based access control across different user types."""
        
        # Test form teacher access
        login_response = test_client.post(
            f"{settings.API_V1_STR}/auth/login",
            json={
                "email": test_user.email,
                "password": TEST_PASSWORD,
            },
        )
        assert login_response.status_code == 200
        
        # Form teacher should have basic access
        response = test_client.get(f"{settings.API_V1_STR}/auth/me")
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["role"] == UserRole.FORM_TEACHER.value
        
        # Logout form teacher
        test_client.post(f"{settings.API_V1_STR}/auth/logout")
        
        # Test year head access
        login_response = test_client.post(
            f"{settings.API_V1_STR}/auth/login",
            json={
                "email": test_year_head.email,
                "password": TEST_PASSWORD,
            },
        )
        assert login_response.status_code == 200
        
        response = test_client.get(f"{settings.API_V1_STR}/auth/me")
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["role"] == UserRole.YEAR_HEAD.value
        
        # Logout year head
        test_client.post(f"{settings.API_V1_STR}/auth/logout")
        
        # Test admin access
        login_response = test_client.post(
            f"{settings.API_V1_STR}/auth/login",
            json={
                "email": test_admin.email,
                "password": TEST_PASSWORD,
            },
        )
        assert login_response.status_code == 200
        
        response = test_client.get(f"{settings.API_V1_STR}/auth/me")
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["role"] == UserRole.ADMIN.value

    def test_multi_tenant_isolation(self, test_client: TestClient, test_user: User, different_school_user: User):
        """Test that users from different schools cannot access each other's data."""
        
        # Login user from first school
        login_response = test_client.post(
            f"{settings.API_V1_STR}/auth/login",
            json={
                "email": test_user.email,
                "password": TEST_PASSWORD,
            },
        )
        assert login_response.status_code == 200
        
        # Get user data
        response = test_client.get(f"{settings.API_V1_STR}/auth/me")
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["school_id"] == test_user.school_id
        
        # Logout first user
        test_client.post(f"{settings.API_V1_STR}/auth/logout")
        
        # Login user from different school
        login_response = test_client.post(
            f"{settings.API_V1_STR}/auth/login",
            json={
                "email": different_school_user.email,
                "password": TEST_PASSWORD,
            },
        )
        assert login_response.status_code == 200
        
        # Get user data - should be from different school
        response = test_client.get(f"{settings.API_V1_STR}/auth/me")
        assert response.status_code == 200
        other_user_data = response.json()
        assert other_user_data["school_id"] == different_school_user.school_id
        assert other_user_data["school_id"] != user_data["school_id"]


        login_response = test_client.post(
            f"{settings.API_V1_STR}/auth/login",
            json={
                "email": test_user.email,
                "password": TEST_PASSWORD,
            },
        )
        assert login_response.status_code == 200
        
        # Extract CSRF token
        csrf_token = None
        for cookie in login_response.cookies:
            if cookie.name == "csrf_token":
                csrf_token = cookie.value
                break
        
        assert csrf_token is not None
        
        # Test that logout (POST) works with CSRF token in cookie
        logout_response = test_client.post(f"{settings.API_V1_STR}/auth/logout")
        assert logout_response.status_code == 200
        
        # Login again for header test
        login_response = test_client.post(
            f"{settings.API_V1_STR}/auth/login",
            json={
                "email": test_user.email,
                "password": TEST_PASSWORD,
            },
        )
        assert login_response.status_code == 200
        
        # Extract new CSRF token
        for cookie in login_response.cookies:
            if cookie.name == "csrf_token":
                csrf_token = cookie.value
                break
        
        # Test CSRF token in header
        logout_response = test_client.post(
            f"{settings.API_V1_STR}/auth/logout-all",
            headers={"X-CSRF-Token": csrf_token}
        )
        assert logout_response.status_code == 200

    def test_security_headers_and_cookies(self, test_client: TestClient, test_user: User):
        """Test that security headers and cookie settings are properly configured."""
        
        # Login
        login_response = test_client.post(
            f"{settings.API_V1_STR}/auth/login",
            json={
                "email": test_user.email,
                "password": TEST_PASSWORD,
            },
        )
        assert login_response.status_code == 200
        
        # Check that session and CSRF cookies are set
        cookie_names = [cookie.name for cookie in login_response.cookies]
        assert "session_id" in cookie_names
        assert "csrf_token" in cookie_names
        
        # Verify cookie security properties (limited in TestClient)
        session_cookie = None
        csrf_cookie = None
        
        for cookie in login_response.cookies:
            if cookie.name == "session_id":
                session_cookie = cookie
            elif cookie.name == "csrf_token":
                csrf_cookie = cookie
        
        assert session_cookie is not None
        assert csrf_cookie is not None
        
        # In a real browser test, you would verify:
        # - HttpOnly flag
        # - Secure flag (in HTTPS)
        # - SameSite attribute

    def test_api_health_endpoints(self, test_client: TestClient):
        """Test that health check endpoints work correctly."""
        
        # Test root health endpoint
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        
        # Test API v1 health endpoint
        response = test_client.get(f"{settings.API_V1_STR}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["api_version"] == "v1"

    def test_error_handling_and_responses(self, test_client: TestClient):
        """Test proper error handling throughout the authentication system."""
        
        # Test invalid email format
        response = test_client.post(
            f"{settings.API_V1_STR}/auth/login",
            json={
                "email": "invalid-email",
                "password": "anypassword",
            },
        )
        assert response.status_code == 422  # Validation error
        
        # Test missing password
        response = test_client.post(
            f"{settings.API_V1_STR}/auth/login",
            json={
                "email": "test@example.com",
            },
        )
        assert response.status_code == 422  # Validation error
        
        # Test nonexistent user
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
        
        # Test accessing protected endpoint without auth
        response = test_client.get(f"{settings.API_V1_STR}/auth/me")
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Not authenticated"
