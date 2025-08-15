from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class TeacherClassAssignment(BaseModel):
    __tablename__ = "teacher_class_assignments"
    __table_args__ = (UniqueConstraint("teacher_id", "class_id", name="_teacher_class_uc"),)

    # Foreign keys
    teacher_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    class_id: Mapped[int] = mapped_column(ForeignKey("classes.id"), nullable=False, index=True)

    # Relationships
    teacher: Mapped["User"] = relationship(back_populates="class_assignments")
    class_obj: Mapped["Class"] = relationship(back_populates="teacher_assignments")
