from typing import List

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Class(BaseModel):
    __tablename__ = "classes"

    name: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., "Primary 4A"
    level: Mapped[int] = mapped_column(nullable=False)  # e.g., 4 for Primary 4
    section: Mapped[str] = mapped_column(String(10), nullable=False)  # e.g., "A"
    academic_year: Mapped[int] = mapped_column(nullable=False)  # e.g., 2024

    # Multi-tenant field
    school_id: Mapped[int] = mapped_column(ForeignKey("schools.id"), nullable=False, index=True)

    # Relationships
    school: Mapped["School"] = relationship(back_populates="classes")
    students: Mapped[List["Student"]] = relationship(
        back_populates="class_obj", cascade="all, delete-orphan"
    )
    teacher_assignments: Mapped[List["TeacherClassAssignment"]] = relationship(
        back_populates="class_obj", cascade="all, delete-orphan"
    )
