import os
import pytest
from datetime import datetime, timedelta

from app.models import User, Session as UserSession
from app.services import AuthService

# Security-compliant credential management - ONLY from environment
TEST_PASSWORD = os.getenv("SEED_DEFAULT_PASSWORD")
if not TEST_PASSWORD:
    pytest.skip("SEED_DEFAULT_PASSWORD environment variable not set", allow_module_level=True)


class TestAuthService:
    """Test cases for AuthService."""

    def test_authenticate_user_success(self, auth_service: AuthService, test_user: User):
        """Test successful user authentication."""
        authenticated_user = auth_service.authenticate_user(
            email=test_user.email,
            password=TEST_PASSWORD
        )
        
        assert authenticated_user is not None
        assert authenticated_user.id == test_user.id
        assert authenticated_user.email == test_user.email

    def test_authenticate_user_wrong_password(self, auth_service: AuthService, test_user: User):
        """Test authentication with wrong password."""
        authenticated_user = auth_service.authenticate_user(
            email=test_user.email,
            password="invalid_test_password"
        )
        
        assert authenticated_user is None

    def test_authenticate_user_nonexistent_email(self, auth_service: AuthService):
        """Test authentication with non-existent email."""
        authenticated_user = auth_service.authenticate_user(
            email="nonexistent@example.com",
            password="invalid_test_password"
        )
        
        assert authenticated_user is None

    def test_create_session(self, auth_service: AuthService, test_user: User):
        """Test session creation."""
        session = auth_service.create_session(
            user=test_user,
            user_agent="Test Browser",
            ip_address="192.168.1.100"
        )
        
        assert session is not None
        assert session.user_id == test_user.id
        assert session.user_agent == "Test Browser"
        assert session.ip_address == "192.168.1.100"
        assert session.csrf_token is not None
        assert len(session.csrf_token) > 0
        assert session.expires_at > datetime.utcnow()

    def test_get_session_valid(self, auth_service: AuthService, test_session: UserSession):
        """Test retrieving a valid session."""
        retrieved_session = auth_service.get_session(test_session.id)
        
        assert retrieved_session is not None
        assert retrieved_session.id == test_session.id
        assert retrieved_session.user_id == test_session.user_id

    def test_get_session_nonexistent(self, auth_service: AuthService):
        """Test retrieving a non-existent session."""
        retrieved_session = auth_service.get_session("nonexistent_session_id")
        
        assert retrieved_session is None

    def test_get_session_expired(self, auth_service: AuthService, expired_session: UserSession):
        """Test retrieving an expired session."""
        retrieved_session = auth_service.get_session(expired_session.id)
        
        # Should return None and clean up the expired session
        assert retrieved_session is None

    def test_get_session_with_user(self, auth_service: AuthService, test_session: UserSession, test_user: User):
        """Test retrieving session with user data."""
        result = auth_service.get_session_with_user(test_session.id)
        
        assert result is not None
        session, user = result
        assert session.id == test_session.id
        assert user.id == test_user.id
        assert user.email == test_user.email

    def test_get_session_with_user_expired(self, auth_service: AuthService, expired_session: UserSession):
        """Test retrieving expired session with user data."""
        result = auth_service.get_session_with_user(expired_session.id)
        
        # Should return None and clean up the expired session
        assert result is None

    def test_delete_session(self, auth_service: AuthService, test_session: UserSession):
        """Test session deletion."""
        # Verify session exists
        assert auth_service.get_session(test_session.id) is not None
        
        # Delete session
        deleted = auth_service.delete_session(test_session.id)
        assert deleted is True
        
        # Verify session no longer exists
        assert auth_service.get_session(test_session.id) is None

    def test_delete_nonexistent_session(self, auth_service: AuthService):
        """Test deleting a non-existent session."""
        deleted = auth_service.delete_session("nonexistent_session_id")
        assert deleted is False

    def test_delete_user_sessions(self, auth_service: AuthService, test_user: User):
        """Test deleting all sessions for a user."""
        # Create multiple sessions for the user
        session1 = auth_service.create_session(test_user, "Browser 1", "IP 1")
        session2 = auth_service.create_session(test_user, "Browser 2", "IP 2")
        session3 = auth_service.create_session(test_user, "Browser 3", "IP 3")
        
        # Verify sessions exist
        assert auth_service.get_session(session1.id) is not None
        assert auth_service.get_session(session2.id) is not None
        assert auth_service.get_session(session3.id) is not None
        
        # Delete all user sessions
        deleted_count = auth_service.delete_user_sessions(test_user.id)
        assert deleted_count == 3
        
        # Verify sessions no longer exist
        assert auth_service.get_session(session1.id) is None
        assert auth_service.get_session(session2.id) is None
        assert auth_service.get_session(session3.id) is None

    def test_cleanup_expired_sessions(self, auth_service: AuthService, db_session, test_user: User):
        """Test cleanup of expired sessions."""
        from app.core.security import generate_session_id, generate_csrf_token
        
        # Create a mix of valid and expired sessions
        valid_session = auth_service.create_session(test_user, "Valid Browser", "Valid IP")
        
        expired_session1 = UserSession(
            id=generate_session_id(),
            user_id=test_user.id,
            expires_at=datetime.utcnow() - timedelta(hours=1),
            csrf_token=generate_csrf_token(),
            user_agent="Expired Browser 1",
            ip_address="Expired IP 1",
        )
        expired_session2 = UserSession(
            id=generate_session_id(),
            user_id=test_user.id,
            expires_at=datetime.utcnow() - timedelta(hours=2),
            csrf_token=generate_csrf_token(),
            user_agent="Expired Browser 2",
            ip_address="Expired IP 2",
        )
        
        db_session.add(expired_session1)
        db_session.add(expired_session2)
        db_session.commit()
        
        # Store IDs for later verification
        expired_session1_id = expired_session1.id
        expired_session2_id = expired_session2.id
        
        # Cleanup expired sessions
        deleted_count = auth_service.cleanup_expired_sessions()
        assert deleted_count == 2
        
        # Verify valid session still exists
        assert auth_service.get_session(valid_session.id) is not None
        
        # Verify expired sessions are gone
        assert auth_service.get_session(expired_session1_id) is None
        assert auth_service.get_session(expired_session2_id) is None

    def test_extend_session(self, auth_service: AuthService, test_session: UserSession):
        """Test extending session expiration."""
        original_expiry = test_session.expires_at
        
        # Extend session
        extended_session = auth_service.extend_session(test_session.id)
        
        assert extended_session is not None
        assert extended_session.expires_at > original_expiry
        assert extended_session.id == test_session.id

    def test_extend_nonexistent_session(self, auth_service: AuthService):
        """Test extending a non-existent session."""
        extended_session = auth_service.extend_session("nonexistent_session_id")
        assert extended_session is None

    def test_validate_csrf_token_valid(self, auth_service: AuthService, test_session: UserSession):
        """Test CSRF token validation with valid token."""
        is_valid = auth_service.validate_csrf_token(test_session.id, test_session.csrf_token)
        assert is_valid is True

    def test_validate_csrf_token_invalid(self, auth_service: AuthService, test_session: UserSession):
        """Test CSRF token validation with invalid token."""
        is_valid = auth_service.validate_csrf_token(test_session.id, "invalid_csrf_token")
        assert is_valid is False

    def test_validate_csrf_token_nonexistent_session(self, auth_service: AuthService):
        """Test CSRF token validation with non-existent session."""
        is_valid = auth_service.validate_csrf_token("nonexistent_session_id", "any_token")
        assert is_valid is False

    def test_session_multi_tenant_isolation(
        self, 
        auth_service: AuthService, 
        test_user: User, 
        different_school_user: User
    ):
        """Test that sessions are properly isolated between schools."""
        # Create sessions for users from different schools
        session1 = auth_service.create_session(test_user, "Browser 1", "IP 1")
        session2 = auth_service.create_session(different_school_user, "Browser 2", "IP 2")
        
        # Each user should only be able to access their own session
        result1 = auth_service.get_session_with_user(session1.id)
        result2 = auth_service.get_session_with_user(session2.id)
        
        assert result1 is not None
        assert result2 is not None
        
        session_1, user_1 = result1
        session_2, user_2 = result2
        
        # Verify sessions belong to correct users and schools
        assert user_1.id == test_user.id
        assert user_1.school_id == test_user.school_id
        assert user_2.id == different_school_user.id
        assert user_2.school_id == different_school_user.school_id
        assert user_1.school_id != user_2.school_id