from enum import Enum
from typing import List, Optional

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class PerformanceBand(str, Enum):
    OUTSTANDING = "outstanding"
    GOOD = "good"
    SATISFACTORY = "satisfactory"
    NEEDS_IMPROVEMENT = "needs_improvement"


class ReportCard(BaseModel):
    __tablename__ = "report_cards"

    # Performance data
    performance_band: Mapped[Optional[PerformanceBand]] = mapped_column(SQLEnum(PerformanceBand))
    overall_average: Mapped[Optional[float]] = mapped_column()

    # Comments
    behavioral_comment: Mapped[Optional[str]] = mapped_column(Text)
    teacher_comment: Mapped[Optional[str]] = mapped_column(Text)

    # PDF storage
    pdf_path: Mapped[Optional[str]] = mapped_column(String(255))

    # Foreign keys
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False, index=True)
    term_id: Mapped[int] = mapped_column(ForeignKey("terms.id"), nullable=False, index=True)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Relationships
    student: Mapped["Student"] = relationship(back_populates="report_cards")
    term: Mapped["Term"] = relationship(back_populates="report_cards")
    created_by: Mapped["User"] = relationship()
    achievements: Mapped[List["Achievement"]] = relationship(
        back_populates="report_card", cascade="all, delete-orphan"
    )
    components: Mapped[List["ReportComponent"]] = relationship(
        back_populates="report_card", cascade="all, delete-orphan"
    )


class ReportComponent(BaseModel):
    __tablename__ = "report_components"

    component_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # e.g., "header", "grades", "achievements"
    content: Mapped[Optional[str]] = mapped_column(Text)
    position: Mapped[int] = mapped_column(nullable=False)

    # Foreign key
    report_card_id: Mapped[int] = mapped_column(ForeignKey("report_cards.id"), nullable=False)

    # Relationships
    report_card: Mapped["ReportCard"] = relationship(back_populates="components")
