from typing import List, Optional

from sqlalchemy import DECIMAL, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class AchievementCategory(BaseModel):
    __tablename__ = "achievement_categories"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Trigger conditions
    min_improvement_percent: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 2))
    min_score: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 2))

    # Relationships
    achievements: Mapped[List["Achievement"]] = relationship(
        back_populates="category", cascade="all, delete-orphan"
    )


class Achievement(BaseModel):
    __tablename__ = "achievements"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Foreign keys
    category_id: Mapped[int] = mapped_column(
        ForeignKey("achievement_categories.id"), nullable=False
    )
    report_card_id: Mapped[int] = mapped_column(ForeignKey("report_cards.id"), nullable=False)

    # Relationships
    category: Mapped["AchievementCategory"] = relationship(back_populates="achievements")
    report_card: Mapped["ReportCard"] = relationship(back_populates="achievements")
