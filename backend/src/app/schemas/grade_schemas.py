from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class SubjectInfoResponse(BaseModel):
    """Basic subject information for grade response."""

    id: int
    name: str
    code: str

    class Config:
        from_attributes = True


class TermInfoResponse(BaseModel):
    """Basic term information for grade response."""

    id: int
    name: str
    term_number: int
    academic_year: int

    class Config:
        from_attributes = True


class ModifiedByInfoResponse(BaseModel):
    """User information for who modified the grade."""

    id: int
    username: str
    full_name: str

    class Config:
        from_attributes = True


class GradeResponse(BaseModel):
    """Standard grade response."""

    id: int
    score: Decimal
    student_id: int
    term_id: int
    subject_id: int
    modified_by_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    subject: SubjectInfoResponse
    term: TermInfoResponse
    modified_by: Optional[ModifiedByInfoResponse] = None

    class Config:
        from_attributes = True


class GradeUpdateRequest(BaseModel):
    """Request model for updating grades."""

    grades: Dict[int, Decimal] = Field(..., description="Dictionary mapping subject_id to score")

    @validator("grades")
    def validate_scores(cls, v):
        """Validate that all scores are between 0 and 100."""
        for subject_id, score in v.items():
            if not isinstance(subject_id, int) or subject_id <= 0:
                raise ValueError(f"Invalid subject_id: {subject_id}")
            if not (0 <= score <= 100):
                raise ValueError(
                    f"Score {score} for subject {subject_id} must be between 0 and 100"
                )
        return v


class StudentGradesResponse(BaseModel):
    """Response for student grades in a specific term."""

    student_id: int
    term_id: int
    grades: List[GradeResponse]
    average_score: Optional[float] = None
    performance_band: Optional[str] = None
    total_subjects: int

    class Config:
        from_attributes = True


class GradeUpdateResponse(BaseModel):
    """Response for grade update operations."""

    success: bool
    message: str
    updated_grades: Optional[List[GradeResponse]] = None
    error: Optional[str] = None


class GradeHistoryResponse(BaseModel):
    """Response for grade history over multiple terms."""

    student_id: int
    subject_id: int
    subject: SubjectInfoResponse
    grades: List[GradeResponse]
    improvement: Optional[Dict[str, Any]] = None


class GradeSummaryResponse(BaseModel):
    """Summary response for multiple students' grades."""

    total_students: int
    total_grades: int
    students: List[Dict[str, Any]]
    term_filter: Optional[int] = None


class PerformanceStatsResponse(BaseModel):
    """Performance statistics response."""

    total_students: int
    performance_bands: Dict[str, int]
    average_score: float
    highest_score: float
    lowest_score: float
    subject_averages: Dict[str, float]


class ImprovementResponse(BaseModel):
    """Grade improvement analysis response."""

    student_id: int
    subject_id: int
    first_score: float
    latest_score: float
    improvement_amount: float
    improvement_percentage: float
    total_terms: int
    first_term: str
    latest_term: str
