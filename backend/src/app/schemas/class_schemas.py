from typing import List, Optional

from pydantic import BaseModel

from app.schemas.student_schemas import StudentBaseResponse


class ClassBaseResponse(BaseModel):
    """Base class response with common fields."""

    id: int
    name: str
    level: int
    section: str
    academic_year: int
    school_id: int

    class Config:
        from_attributes = True


class SchoolInfoResponse(BaseModel):
    """Basic school information for class response."""

    id: int
    name: str

    class Config:
        from_attributes = True


class TeacherInfoResponse(BaseModel):
    """Teacher information for class assignments."""

    id: int
    username: str
    full_name: str
    email: str

    class Config:
        from_attributes = True


class TeacherAssignmentResponse(BaseModel):
    """Teacher assignment response."""

    id: int
    teacher_id: int
    class_id: int
    teacher: TeacherInfoResponse

    class Config:
        from_attributes = True


class ClassResponse(ClassBaseResponse):
    """Standard class response with school info."""

    school: SchoolInfoResponse
    student_count: Optional[int] = None


class ClassDetailResponse(ClassBaseResponse):
    """Detailed class response with students and teachers."""

    school: SchoolInfoResponse
    students: List[StudentBaseResponse] = []
    teacher_assignments: List[TeacherAssignmentResponse] = []


class ClassStudentResponse(BaseModel):
    """Response for students in a class."""

    class_info: ClassBaseResponse
    students: List[StudentBaseResponse]
    total_students: int

    class Config:
        from_attributes = True


class ClassSummaryResponse(BaseModel):
    """Class summary with statistics."""

    id: int
    name: str
    level: int
    section: str
    total_students: int
    average_class_score: Optional[float] = None
    performance_distribution: Optional[dict] = None

    class Config:
        from_attributes = True
