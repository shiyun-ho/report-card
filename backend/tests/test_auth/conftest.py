import asyncio
import os
from datetime import datetime, timedelta
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.core.database import Base, get_db
from app.core.security import get_password_hash
from app.main import app
from app.models import School, User, UserRole, Session as UserSession
from app.services import AuthService

# Import all models to ensure they're registered with Base.metadata
from app.models import *  # noqa: F403,F401

# Security-compliant credential management - ONLY from environment
TEST_PASSWORD = os.getenv("SEED_DEFAULT_PASSWORD")
if not TEST_PASSWORD:
    pytest.skip("SEED_DEFAULT_PASSWORD environment variable not set", allow_module_level=True)

# Security-compliant: Use PostgreSQL like the main app, not SQLite
TEST_DATABASE_URL = os.getenv("DATABASE_URL")
if not TEST_DATABASE_URL:
    pytest.skip("DATABASE_URL environment variable not set", allow_module_level=True)

# Create test engine and session (PostgreSQL, not SQLite)
test_engine = create_engine(
    TEST_DATABASE_URL,
    echo=False,  # Set to True for SQL debugging
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Create a database session for testing with proper cleanup.
    Uses the actual PostgreSQL database with seeded data.
    """
    # Create session (don't create/drop tables - use existing schema)
    session = TestSessionLocal()
    
    # Clean up any existing test data before starting
    try:
        # Delete test data in correct order (respecting foreign keys)
        session.execute("DELETE FROM user_sessions WHERE user_id IN (SELECT id FROM users WHERE email LIKE '%@testschool.edu' OR email LIKE '%@otherschool.edu')")
        session.execute("DELETE FROM teacher_class_assignments WHERE teacher_id IN (SELECT id FROM users WHERE email LIKE '%@testschool.edu' OR email LIKE '%@otherschool.edu')")
        session.execute("DELETE FROM users WHERE email LIKE '%@testschool.edu' OR email LIKE '%@otherschool.edu'")
        session.execute("DELETE FROM schools WHERE name LIKE 'Test Primary School%' OR name LIKE 'Other School%'")
        session.commit()
    except Exception:
        session.rollback()
    
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        # Clean up after the test
        try:
            session.execute("DELETE FROM user_sessions WHERE user_id IN (SELECT id FROM users WHERE email LIKE '%@testschool.edu' OR email LIKE '%@otherschool.edu')")
            session.execute("DELETE FROM teacher_class_assignments WHERE teacher_id IN (SELECT id FROM users WHERE email LIKE '%@testschool.edu' OR email LIKE '%@otherschool.edu')")
            session.execute("DELETE FROM users WHERE email LIKE '%@testschool.edu' OR email LIKE '%@otherschool.edu')")
            session.execute("DELETE FROM schools WHERE name LIKE 'Test Primary School%' OR name LIKE 'Other School%'")
            session.commit()
        except Exception:
            session.rollback()
        finally:
            session.close()


@pytest.fixture(scope="function")
def test_client(db_session: Session) -> TestClient:
    """
    Create a test client with database dependency override.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client
    
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_school(db_session: Session) -> School:
    """
    Create a test school with unique identifier.
    """
    import uuid
    import time
    import threading
    # Use thread ID + timestamp + UUID for maximum uniqueness
    thread_id = threading.get_ident() % 1000
    timestamp = int(time.time() * 1000000) % 1000000  # microseconds
    uuid_part = str(uuid.uuid4()).replace('-', '')[:8]
    unique_id = f"{thread_id}{timestamp}{uuid_part}"[:12]
    school = School(
        name=f"Test Primary School {unique_id}",
        code=f"TPS{unique_id[:3].upper()}",
        address=f"123 Test Street, Test City {unique_id}",
    )
    db_session.add(school)
    db_session.commit()
    db_session.refresh(school)
    return school


@pytest.fixture(scope="function")
def test_user(db_session: Session, test_school: School) -> User:
    """
    Create a test user (form teacher) with unique identifier.
    """
    import uuid
    import time
    import threading
    # Use thread ID + timestamp + UUID for maximum uniqueness
    thread_id = threading.get_ident() % 1000
    timestamp = int(time.time() * 1000000) % 1000000  # microseconds
    uuid_part = str(uuid.uuid4()).replace('-', '')[:8]
    unique_id = f"{thread_id}{timestamp}{uuid_part}"[:12]
    user = User(
        email=f"teacher{unique_id}@testschool.edu",
        username=f"testteacher{unique_id}",
        full_name=f"Test Teacher {unique_id}",
        hashed_password=get_password_hash(TEST_PASSWORD),
        role=UserRole.FORM_TEACHER,
        school_id=test_school.id,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_year_head(db_session: Session, test_school: School) -> User:
    """
    Create a test year head user with unique identifier.
    """
    import uuid
    import time
    import threading
    # Use thread ID + timestamp + UUID for maximum uniqueness
    thread_id = threading.get_ident() % 1000
    timestamp = int(time.time() * 1000000) % 1000000  # microseconds
    uuid_part = str(uuid.uuid4()).replace('-', '')[:8]
    unique_id = f"{thread_id}{timestamp}{uuid_part}"[:12]
    user = User(
        email=f"yearhead{unique_id}@testschool.edu",
        username=f"testyearhead{unique_id}",
        full_name=f"Test Year Head {unique_id}",
        hashed_password=get_password_hash(TEST_PASSWORD),
        role=UserRole.YEAR_HEAD,
        school_id=test_school.id,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_admin(db_session: Session, test_school: School) -> User:
    """
    Create a test admin user with unique identifier.
    """
    import uuid
    import time
    import threading
    # Use thread ID + timestamp + UUID for maximum uniqueness
    thread_id = threading.get_ident() % 1000
    timestamp = int(time.time() * 1000000) % 1000000  # microseconds
    uuid_part = str(uuid.uuid4()).replace('-', '')[:8]
    unique_id = f"{thread_id}{timestamp}{uuid_part}"[:12]
    user = User(
        email=f"admin{unique_id}@testschool.edu",
        username=f"testadmin{unique_id}",
        full_name=f"Test Admin {unique_id}",
        hashed_password=get_password_hash(TEST_PASSWORD),
        role=UserRole.ADMIN,
        school_id=test_school.id,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def different_school_user(db_session: Session) -> User:
    """
    Create a user from a different school for multi-tenant testing with unique identifier.
    """
    import uuid
    import time
    import threading
    # Use thread ID + timestamp + UUID for maximum uniqueness
    thread_id = threading.get_ident() % 1000
    timestamp = int(time.time() * 1000000) % 1000000  # microseconds
    uuid_part = str(uuid.uuid4()).replace('-', '')[:8]
    unique_id = f"{thread_id}{timestamp}{uuid_part}"[:12]
    
    # Create another school
    other_school = School(
        name=f"Other School {unique_id}",
        code=f"OS{unique_id[:3].upper()}", 
        address=f"456 Other Street, Other City {unique_id}",
    )
    db_session.add(other_school)
    db_session.commit()
    db_session.refresh(other_school)
    
    # Create user in the other school
    user = User(
        email=f"teacher{unique_id}@otherschool.edu",
        username=f"otherteacher{unique_id}",
        full_name=f"Other Teacher {unique_id}",
        hashed_password=get_password_hash(TEST_PASSWORD),
        role=UserRole.FORM_TEACHER,
        school_id=other_school.id,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_service(db_session: Session) -> AuthService:
    """
    Create an AuthService instance with the test database.
    """
    return AuthService(db_session)


@pytest.fixture(scope="function")
def test_session(db_session: Session, test_user: User, auth_service: AuthService) -> UserSession:
    """
    Create a test session for a user.
    """
    session = auth_service.create_session(
        user=test_user,
        user_agent="Test User Agent",
        ip_address="127.0.0.1",
    )
    return session


@pytest.fixture(scope="function")
def expired_session(db_session: Session, test_user: User) -> UserSession:
    """
    Create an expired session for testing.
    """
    from app.core.security import generate_session_id, generate_csrf_token
    
    session = UserSession(
        id=generate_session_id(),
        user_id=test_user.id,
        expires_at=datetime.utcnow() - timedelta(hours=1),  # Expired 1 hour ago
        csrf_token=generate_csrf_token(),
        user_agent="Test User Agent",
        ip_address="127.0.0.1",
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    return session


@pytest.fixture(scope="function") 
def authenticated_client(test_client: TestClient, test_user: User) -> dict:
    """
    Create an authenticated test client with session cookies.
    
    Returns:
        Dictionary with client and session information
    """
    # Login to get session cookies
    response = test_client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={
            "email": test_user.email,
            "password": TEST_PASSWORD,
        },
    )
    
    assert response.status_code == 200
    
    # Extract cookies
    session_id = None
    csrf_token = None
    
    # Cookies might be a dict-like object or list of cookie objects
    if hasattr(response.cookies, 'items'):
        # If it's a dict-like object
        for name, value in response.cookies.items():
            if name == "session_id":
                session_id = value
            elif name == "csrf_token":
                csrf_token = value
    else:
        # If it's a list of cookie objects
        for cookie in response.cookies:
            if hasattr(cookie, 'name'):
                if cookie.name == "session_id":
                    session_id = cookie.value
                elif cookie.name == "csrf_token":
                    csrf_token = cookie.value
    
    return {
        "client": test_client,
        "session_id": session_id,
        "csrf_token": csrf_token,
        "user": test_user,
    }


# Test data fixtures
@pytest.fixture
def valid_login_data():
    """Valid login request data."""
    return {
        "email": "teacher@testschool.edu",
        "password": TEST_PASSWORD,
    }


@pytest.fixture
def invalid_login_data():
    """Invalid login request data."""
    return {
        "email": "teacher@testschool.edu",
        "password": "invalid_test_password",
    }