from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


# Dependency to get DB session
def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    Ensures proper cleanup after request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Database initialization
def init_db():
    """
    Initialize database tables.
    This should be called after all models are imported.
    """
    # Import all models here to ensure they are registered
    # with SQLAlchemy's Base.metadata
    from app.models import (  # noqa
        BaseModel,
        School,
        User,
        Session,
        Class,
        Student,
        Term,
        Subject,
        Grade,
        AchievementCategory,
        Achievement,
        ReportCard,
        ReportComponent,
        TeacherClassAssignment,
    )

    Base.metadata.create_all(bind=engine)


# Test database connection
def test_connection():
    """
    Test database connection.
    """
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
