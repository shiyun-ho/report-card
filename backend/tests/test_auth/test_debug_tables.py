"""Debug test to check what tables are created."""

import pytest
from sqlalchemy import inspect

from app.core.database import Base


def test_debug_tables(db_session):
    """Debug test to see what tables are created."""
    
    # Get the engine from the session
    engine = db_session.bind
    
    # Get inspector
    inspector = inspect(engine)
    
    # List all table names
    table_names = inspector.get_table_names()
    print(f"Tables created: {table_names}")
    
    # List all models registered with Base
    model_classes = [cls.__name__ for cls in Base.registry._class_registry.values() if hasattr(cls, '__tablename__')]
    print(f"Model classes: {model_classes}")
    
    # Check if user_sessions table exists
    assert "user_sessions" in table_names, f"user_sessions table not found. Available tables: {table_names}"