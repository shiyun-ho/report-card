from enum import Enum
from typing import TYPE_CHECKING, List

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.session import Session


class UserRole(str, Enum):
    FORM_TEACHER = "form_teacher"
    YEAR_HEAD = "year_head"
    ADMIN = "admin"


class User(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), nullable=False)

    # Multi-tenant field
    school_id: Mapped[int] = mapped_column(ForeignKey("schools.id"), nullable=False, index=True)

    # Relationships
    school: Mapped["School"] = relationship(back_populates="users")
    class_assignments: Mapped[List["TeacherClassAssignment"]] = relationship(
        back_populates="teacher", cascade="all, delete-orphan"
    )
    sessions: Mapped[List["Session"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
