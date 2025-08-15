from sqlalchemy import Boolean, Column, DateTime, Integer
from sqlalchemy.sql import func

from app.core.database import Base


class BaseModel(Base):
    """
    Base model class with common fields.
    All models should inherit from this class.
    """

    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True, nullable=False)
