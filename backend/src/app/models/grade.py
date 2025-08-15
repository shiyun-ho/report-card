from decimal import Decimal
from typing import Optional

from sqlalchemy import DECIMAL, CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Grade(BaseModel):
    __tablename__ = "grades"
    __table_args__ = (
        UniqueConstraint("student_id", "term_id", "subject_id", name="_student_term_subject_uc"),
        CheckConstraint("score >= 0 AND score <= 100", name="_score_range_check"),
    )

    score: Mapped[Decimal] = mapped_column(DECIMAL(5, 2), nullable=False)

    # Foreign keys
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False, index=True)
    term_id: Mapped[int] = mapped_column(ForeignKey("terms.id"), nullable=False, index=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), nullable=False, index=True)

    # Track who last modified
    modified_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))

    # Relationships
    student: Mapped["Student"] = relationship(back_populates="grades")
    term: Mapped["Term"] = relationship(back_populates="grades")
    subject: Mapped["Subject"] = relationship(back_populates="grades")
    modified_by: Mapped[Optional["User"]] = relationship()
