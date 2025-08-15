from datetime import date
from typing import List

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Term(BaseModel):
    __tablename__ = "terms"

    name: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., "Term 1 2024"
    academic_year: Mapped[int] = mapped_column(nullable=False)
    term_number: Mapped[int] = mapped_column(nullable=False)  # 1, 2, 3, or 4
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Multi-tenant field
    school_id: Mapped[int] = mapped_column(ForeignKey("schools.id"), nullable=False, index=True)

    # Relationships
    school: Mapped["School"] = relationship(back_populates="terms")
    grades: Mapped[List["Grade"]] = relationship(
        back_populates="term", cascade="all, delete-orphan"
    )
    report_cards: Mapped[List["ReportCard"]] = relationship(
        back_populates="term", cascade="all, delete-orphan"
    )
