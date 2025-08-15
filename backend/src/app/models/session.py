from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User


class Session(BaseModel):
    """
    User session model for session-based authentication.

    Stores session data in PostgreSQL with security tracking.
    """

    __tablename__ = "user_sessions"

    # Override id to be string (hashed session token) instead of integer
    id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)

    # Foreign key to user
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    # Session lifecycle
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    # Security tracking
    csrf_token: Mapped[str] = mapped_column(String(64), nullable=False)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)  # Support IPv6

    # Relationship back to user
    user: Mapped["User"] = relationship(back_populates="sessions")
