import pytest
from fastapi import FastAPI, Depends, HTTPException
from fastapi.testclient import TestClient

from app.dependencies.auth import (
    get_current_user,
    get_current_user_optional,
    get_current_user_school_id,
    require_admin,
    require_form_teacher,
    require_year_head,
    require_year_head_or_admin,
    verify_csrf_token,
    SchoolIsolationDependency,
)
from app.models import User, UserRole


# Test app for dependency testing
test_app = FastAPI()


@test_app.get("/protected")
async def protected_endpoint(current_user: User = Depends(get_current_user)):
    return {"user_id": current_user.id, "email": current_user.email}


@test_app.get("/optional")
async def optional_endpoint(current_user: User = Depends(get_current_user_optional)):
    if current_user:
        return {"user_id": current_user.id, "authenticated": True}
    return {"authenticated": False}


@test_app.get("/school-id")
async def school_id_endpoint(school_id: int = Depends(get_current_user_school_id)):
    return {"school_id": school_id}


@test_app.get("/form-teacher-only")
async def form_teacher_endpoint(current_user: User = Depends(require_form_teacher)):
    return {"user_id": current_user.id, "role": current_user.role.value}


@test_app.get("/year-head-only")
async def year_head_endpoint(current_user: User = Depends(require_year_head)):
    return {"user_id": current_user.id, "role": current_user.role.value}


@test_app.get("/year-head-or-admin")
async def year_head_or_admin_endpoint(current_user: User = Depends(require_year_head_or_admin)):
    return {"user_id": current_user.id, "role": current_user.role.value}


@test_app.get("/admin-only")
async def admin_endpoint(current_user: User = Depends(require_admin)):
    return {"user_id": current_user.id, "role": current_user.role.value}


@test_app.post("/csrf-protected")
async def csrf_protected_endpoint(
    valid: bool = Depends(verify_csrf_token),
    current_user: User = Depends(get_current_user),
):
    return {"csrf_valid": valid, "user_id": current_user.id}


@test_app.get("/school-isolated")
async def school_isolated_endpoint(school_id: int = Depends(SchoolIsolationDependency())):
    return {"allowed_school_id": school_id}


class TestAuthDependencies:
    """Test cases for authentication dependencies."""

    @pytest.fixture
    def dependency_client(self, db_session):
        """Create a test client for dependency testing."""
        from app.core.database import get_db
        
        def override_get_db():
            try:
                yield db_session
            finally:
                pass
        
        test_app.dependency_overrides[get_db] = override_get_db
        
        with TestClient(test_app) as client:
            yield client
        
        test_app.dependency_overrides.clear()

    def test_get_current_user_authenticated(self, dependency_client: TestClient, authenticated_client: dict):
        """Test get_current_user with authenticated user."""
        client = dependency_client
        session_id = authenticated_client["session_id"]
        user = authenticated_client["user"]
        
        # Set session cookie
        client.cookies.set("session_id", session_id)
        
        response = client.get("/protected")
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == user.id
        assert data["email"] == user.email

    def test_get_current_user_not_authenticated(self, dependency_client: TestClient):
        """Test get_current_user without authentication."""
        response = dependency_client.get("/protected")
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Authentication required"

    def test_get_current_user_invalid_session(self, dependency_client: TestClient):
        """Test get_current_user with invalid session."""
        dependency_client.cookies.set("session_id", "invalid_session_id")
        
        response = dependency_client.get("/protected")
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Invalid or expired session"

    def test_get_current_user_optional_authenticated(self, dependency_client: TestClient, authenticated_client: dict):
        """Test get_current_user_optional with authenticated user."""
        client = dependency_client
        session_id = authenticated_client["session_id"]
        user = authenticated_client["user"]
        
        client.cookies.set("session_id", session_id)
        
        response = client.get("/optional")
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == user.id
        assert data["authenticated"] is True

    def test_get_current_user_optional_not_authenticated(self, dependency_client: TestClient):
        """Test get_current_user_optional without authentication."""
        response = dependency_client.get("/optional")
        
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is False

    def test_get_current_user_school_id(self, dependency_client: TestClient, authenticated_client: dict):
        """Test get_current_user_school_id dependency."""
        client = dependency_client
        session_id = authenticated_client["session_id"]
        user = authenticated_client["user"]
        
        client.cookies.set("session_id", session_id)
        
        response = client.get("/school-id")
        
        assert response.status_code == 200
        data = response.json()
        assert data["school_id"] == user.school_id

    def test_require_form_teacher_success(self, dependency_client: TestClient, authenticated_client: dict):
        """Test require_form_teacher with form teacher user."""
        client = dependency_client
        session_id = authenticated_client["session_id"]
        user = authenticated_client["user"]
        
        # Ensure user is form teacher
        assert user.role == UserRole.FORM_TEACHER
        
        client.cookies.set("session_id", session_id)
        
        response = client.get("/form-teacher-only")
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == user.id
        assert data["role"] == UserRole.FORM_TEACHER.value

    def test_require_form_teacher_wrong_role(self, dependency_client: TestClient, test_year_head: User, auth_service):
        """Test require_form_teacher with non-form-teacher user."""
        # Create session for year head
        session = auth_service.create_session(test_year_head)
        
        dependency_client.cookies.set("session_id", session.id)
        
        response = dependency_client.get("/form-teacher-only")
        
        assert response.status_code == 403
        data = response.json()
        assert "Form teacher role required" in data["detail"]

    def test_require_year_head_success(self, dependency_client: TestClient, test_year_head: User, auth_service):
        """Test require_year_head with year head user."""
        session = auth_service.create_session(test_year_head)
        
        dependency_client.cookies.set("session_id", session.id)
        
        response = dependency_client.get("/year-head-only")
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == test_year_head.id
        assert data["role"] == UserRole.YEAR_HEAD.value

    def test_require_year_head_wrong_role(self, dependency_client: TestClient, authenticated_client: dict):
        """Test require_year_head with non-year-head user."""
        client = dependency_client
        session_id = authenticated_client["session_id"]
        user = authenticated_client["user"]
        
        # Ensure user is not year head
        assert user.role != UserRole.YEAR_HEAD
        
        client.cookies.set("session_id", session_id)
        
        response = client.get("/year-head-only")
        
        assert response.status_code == 403
        data = response.json()
        assert "Year head role required" in data["detail"]

    def test_require_year_head_or_admin_year_head(self, dependency_client: TestClient, test_year_head: User, auth_service):
        """Test require_year_head_or_admin with year head user."""
        session = auth_service.create_session(test_year_head)
        
        dependency_client.cookies.set("session_id", session.id)
        
        response = dependency_client.get("/year-head-or-admin")
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == test_year_head.id
        assert data["role"] == UserRole.YEAR_HEAD.value

    def test_require_year_head_or_admin_admin(self, dependency_client: TestClient, test_admin: User, auth_service):
        """Test require_year_head_or_admin with admin user."""
        session = auth_service.create_session(test_admin)
        
        dependency_client.cookies.set("session_id", session.id)
        
        response = dependency_client.get("/year-head-or-admin")
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == test_admin.id
        assert data["role"] == UserRole.ADMIN.value

    def test_require_year_head_or_admin_wrong_role(self, dependency_client: TestClient, authenticated_client: dict):
        """Test require_year_head_or_admin with form teacher user."""
        client = dependency_client
        session_id = authenticated_client["session_id"]
        user = authenticated_client["user"]
        
        # Ensure user is form teacher (not year head or admin)
        assert user.role == UserRole.FORM_TEACHER
        
        client.cookies.set("session_id", session_id)
        
        response = client.get("/year-head-or-admin")
        
        assert response.status_code == 403
        data = response.json()
        assert "Year head or admin role required" in data["detail"]

    def test_require_admin_success(self, dependency_client: TestClient, test_admin: User, auth_service):
        """Test require_admin with admin user."""
        session = auth_service.create_session(test_admin)
        
        dependency_client.cookies.set("session_id", session.id)
        
        response = dependency_client.get("/admin-only")
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == test_admin.id
        assert data["role"] == UserRole.ADMIN.value

    def test_require_admin_wrong_role(self, dependency_client: TestClient, authenticated_client: dict):
        """Test require_admin with non-admin user."""
        client = dependency_client
        session_id = authenticated_client["session_id"]
        user = authenticated_client["user"]
        
        # Ensure user is not admin
        assert user.role != UserRole.ADMIN
        
        client.cookies.set("session_id", session_id)
        
        response = client.get("/admin-only")
        
        assert response.status_code == 403
        data = response.json()
        assert "Admin role required" in data["detail"]

    def test_verify_csrf_token_valid(self, dependency_client: TestClient, authenticated_client: dict):
        """Test CSRF token verification with valid token."""
        client = dependency_client
        session_id = authenticated_client["session_id"]
        csrf_token = authenticated_client["csrf_token"]
        user = authenticated_client["user"]
        
        client.cookies.set("session_id", session_id)
        client.cookies.set("csrf_token", csrf_token)
        
        response = client.post("/csrf-protected")
        
        assert response.status_code == 200
        data = response.json()
        assert data["csrf_valid"] is True
        assert data["user_id"] == user.id

    def test_verify_csrf_token_invalid(self, dependency_client: TestClient, authenticated_client: dict):
        """Test CSRF token verification with invalid token."""
        client = dependency_client
        session_id = authenticated_client["session_id"]
        
        client.cookies.set("session_id", session_id)
        client.cookies.set("csrf_token", "invalid_csrf_token")
        
        response = client.post("/csrf-protected")
        
        assert response.status_code == 403
        data = response.json()
        assert "Invalid CSRF token" in data["detail"]

    def test_verify_csrf_token_missing(self, dependency_client: TestClient, authenticated_client: dict):
        """Test CSRF token verification with missing token."""
        client = dependency_client
        session_id = authenticated_client["session_id"]
        
        client.cookies.set("session_id", session_id)
        # Don't set CSRF token
        
        response = client.post("/csrf-protected")
        
        assert response.status_code == 403
        data = response.json()
        assert "CSRF token required" in data["detail"]

    def test_verify_csrf_token_header(self, dependency_client: TestClient, authenticated_client: dict):
        """Test CSRF token verification via header."""
        client = dependency_client
        session_id = authenticated_client["session_id"]
        csrf_token = authenticated_client["csrf_token"]
        user = authenticated_client["user"]
        
        client.cookies.set("session_id", session_id)
        
        # Send CSRF token in header instead of cookie
        response = client.post(
            "/csrf-protected",
            headers={"X-CSRF-Token": csrf_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["csrf_valid"] is True
        assert data["user_id"] == user.id

    def test_school_isolation_dependency(self, dependency_client: TestClient, authenticated_client: dict):
        """Test school isolation dependency."""
        client = dependency_client
        session_id = authenticated_client["session_id"]
        user = authenticated_client["user"]
        
        client.cookies.set("session_id", session_id)
        
        response = client.get("/school-isolated")
        
        assert response.status_code == 200
        data = response.json()
        assert data["allowed_school_id"] == user.school_id

    def test_session_extension_in_dependencies(self, dependency_client: TestClient, authenticated_client: dict, db_session):
        """Test that dependencies automatically extend sessions."""
        from app.services import AuthService
        
        client = dependency_client
        session_id = authenticated_client["session_id"]
        
        # Get initial session expiry
        auth_service = AuthService(db_session)
        initial_session = auth_service.get_session(session_id)
        initial_expiry = initial_session.expires_at
        
        client.cookies.set("session_id", session_id)
        
        # Make request (should extend session via dependency)
        response = client.get("/protected")
        assert response.status_code == 200
        
        # Check that session was extended
        extended_session = auth_service.get_session(session_id)
        assert extended_session.expires_at > initial_expiry

    def test_multi_tenant_isolation_via_dependencies(
        self, 
        dependency_client: TestClient, 
        authenticated_client: dict,
        different_school_user: User,
        auth_service
    ):
        """Test that dependencies enforce multi-tenant isolation."""
        # Create session for user from different school
        other_session = auth_service.create_session(different_school_user)
        
        # Try to use the other user's session
        dependency_client.cookies.set("session_id", other_session.id)
        
        response = dependency_client.get("/school-isolated")
        
        assert response.status_code == 200
        data = response.json()
        # Should return the other user's school ID (isolation working correctly)
        assert data["allowed_school_id"] == different_school_user.school_id
        assert data["allowed_school_id"] != authenticated_client["user"].school_id