from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Subject(BaseModel):
    __tablename__ = "subjects"

    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)

    # Relationships
    grades: Mapped[List["Grade"]] = relationship(
        back_populates="subject", cascade="all, delete-orphan"
    )
