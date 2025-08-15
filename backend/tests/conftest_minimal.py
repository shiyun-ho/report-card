"""Minimal test configuration without main app import to avoid WeasyPrint issues."""
import asyncio
import os
from typing import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.models import *  # noqa: F403,F401

# Security-compliant credential management - ONLY from environment
SEED_DEFAULT_PASSWORD = os.getenv("SEED_DEFAULT_PASSWORD")
if not SEED_DEFAULT_PASSWORD:
    pytest.skip("SEED_DEFAULT_PASSWORD environment variable not set", allow_module_level=True)

# Security-compliant: Use environment variable without fallback
TEST_DATABASE_URL = os.getenv("DATABASE_URL")
if not TEST_DATABASE_URL:
    pytest.skip("DATABASE_URL environment variable not set", allow_module_level=True)

# Create test engine and session
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
    Create a database session for testing.
    Uses the actual development database with seeded data.
    """
    # Create session
    session = TestSessionLocal()
    
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def seed_default_password() -> str:
    """Provide the seed default password for testing."""
    return SEED_DEFAULT_PASSWORD