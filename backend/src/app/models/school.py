from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class School(BaseModel):
    __tablename__ = "schools"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    address: Mapped[str] = mapped_column(String(255))

    # Relationships
    users: Mapped[List["User"]] = relationship(
        back_populates="school", cascade="all, delete-orphan"
    )
    classes: Mapped[List["Class"]] = relationship(
        back_populates="school", cascade="all, delete-orphan"
    )
    students: Mapped[List["Student"]] = relationship(
        back_populates="school", cascade="all, delete-orphan"
    )
    terms: Mapped[List["Term"]] = relationship(
        back_populates="school", cascade="all, delete-orphan"
    )
