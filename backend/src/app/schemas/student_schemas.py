from datetime import date
from typing import List, Optional

from pydantic import BaseModel

from app.schemas.grade_schemas import GradeResponse


class StudentBaseResponse(BaseModel):
    """Base student response with common fields."""

    id: int
    student_id: str
    first_name: str
    last_name: str
    full_name: str
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    school_id: int
    class_id: int

    class Config:
        from_attributes = True


class ClassInfoResponse(BaseModel):
    """Basic class information for student response."""

    id: int
    name: str
    level: int
    section: str
    academic_year: int

    class Config:
        from_attributes = True


class SchoolInfoResponse(BaseModel):
    """Basic school information for student response."""

    id: int
    name: str

    class Config:
        from_attributes = True


class StudentResponse(StudentBaseResponse):
    """Standard student response with class and school info."""

    class_obj: ClassInfoResponse
    school: SchoolInfoResponse


class StudentDetailResponse(StudentBaseResponse):
    """Detailed student response with grades."""

    class_obj: ClassInfoResponse
    school: SchoolInfoResponse
    grades: List[GradeResponse] = []


class StudentSummaryResponse(BaseModel):
    """Student summary with grade statistics."""

    id: int
    student_id: str
    full_name: str
    class_name: str
    total_grades: int
    average_score: Optional[float] = None
    performance_band: Optional[str] = None
    latest_term: Optional[str] = None

    class Config:
        from_attributes = True
