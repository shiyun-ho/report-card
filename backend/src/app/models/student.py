from datetime import date
from typing import List, Optional

from sqlalchemy import Date, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Student(BaseModel):
    __tablename__ = "students"
    __table_args__ = (UniqueConstraint("student_id", "school_id", name="_student_school_uc"),)

    student_id: Mapped[str] = mapped_column(String(20), nullable=False)  # School's student ID
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date)
    gender: Mapped[Optional[str]] = mapped_column(String(10))

    # Multi-tenant and foreign keys
    school_id: Mapped[int] = mapped_column(ForeignKey("schools.id"), nullable=False, index=True)
    class_id: Mapped[int] = mapped_column(ForeignKey("classes.id"), nullable=False, index=True)

    # Relationships
    school: Mapped["School"] = relationship(back_populates="students")
    class_obj: Mapped["Class"] = relationship(back_populates="students")
    grades: Mapped[List["Grade"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )
    report_cards: Mapped[List["ReportCard"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
