from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user, verify_csrf_token
from app.models import User
from app.schemas.grade_schemas import (
    GradeHistoryResponse,
    GradeResponse,
    GradeSummaryResponse,
    GradeUpdateRequest,
    GradeUpdateResponse,
    ImprovementResponse,
    PerformanceStatsResponse,
    StudentGradesResponse,
)
from app.services.grade_service import GradeService

router = APIRouter()


@router.get("/students/{student_id}", response_model=List[GradeResponse])
async def get_student_grades(
    student_id: int,
    term_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get grades for a specific student.

    Optionally filter by term_id. If no term_id provided, returns all terms.
    Access controlled by user role and teacher assignments.
    """
    grade_service = GradeService(db)
    grades = grade_service.get_student_grades(student_id, term_id, current_user)

    return [GradeResponse.model_validate(grade) for grade in grades]


@router.get("/students/{student_id}/terms/{term_id}", response_model=StudentGradesResponse)
async def get_student_term_grades(
    student_id: int,
    term_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get comprehensive grade information for a student in a specific term.

    Includes grades, calculated average, and performance band.
    """
    grade_service = GradeService(db)
    grades = grade_service.get_student_grades(student_id, term_id, current_user)

    if not grades:
        # Check if student exists and is accessible
        if not grade_service.can_edit_student_grades(current_user, student_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Student not found or access denied"
            )

    # Calculate statistics
    average_score = None
    performance_band = None
    if grades:
        total_score = sum(float(grade.score) for grade in grades)
        average_score = total_score / len(grades)
        performance_band = grade_service.calculate_performance_band(average_score)

    return StudentGradesResponse(
        student_id=student_id,
        term_id=term_id,
        grades=[GradeResponse.model_validate(grade) for grade in grades],
        average_score=average_score,
        performance_band=performance_band,
        total_subjects=len(grades),
    )


@router.put("/students/{student_id}/terms/{term_id}", response_model=GradeUpdateResponse)
async def update_student_grades(
    student_id: int,
    term_id: int,
    grade_data: GradeUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    csrf_valid: bool = Depends(verify_csrf_token),
):
    """
    Update grades for a student in a specific term.

    Requires CSRF token for security.
    Access controlled by user role and teacher assignments.
    """
    grade_service = GradeService(db)
    result = grade_service.update_student_grades(
        student_id, term_id, grade_data.grades, current_user
    )

    if not result["success"]:
        if "Permission denied" in result["error"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=result["error"])
        elif "not found" in result["error"]:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["error"])
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])

    # Convert grades to response format
    updated_grades = None
    if result.get("grades"):
        updated_grades = [GradeResponse.model_validate(grade) for grade in result["grades"]]

    return GradeUpdateResponse(
        success=result["success"], message=result["message"], updated_grades=updated_grades
    )


@router.get("/summary", response_model=GradeSummaryResponse)
async def get_grade_summary(
    term_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get grade summary for all students accessible to the current user.

    Optionally filter by term_id.
    Useful for dashboard displays and reporting.
    """
    grade_service = GradeService(db)
    summary = grade_service.get_grade_summary(current_user, term_id)

    return GradeSummaryResponse(
        total_students=summary["total_students"],
        total_grades=summary.get("total_grades", 0),
        students=summary["students"],
        term_filter=term_id,
    )


@router.get(
    "/students/{student_id}/subjects/{subject_id}/history", response_model=GradeHistoryResponse
)
async def get_grade_history(
    student_id: int,
    subject_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get grade history for a student in a specific subject across all terms.

    Includes improvement analysis if sufficient data is available.
    """
    grade_service = GradeService(db)
    grades = grade_service.get_grade_history(student_id, subject_id, current_user)

    if not grades:
        # Check if student exists and is accessible
        if not grade_service.can_edit_student_grades(current_user, student_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Student not found or access denied"
            )
        # Return empty history if no grades found
        grades = []

    # Get improvement analysis
    improvement = grade_service.calculate_improvement(student_id, subject_id, current_user)

    # Get subject info from first grade if available
    subject_info = None
    if grades:
        subject_info = grades[0].subject

    return GradeHistoryResponse(
        student_id=student_id,
        subject_id=subject_id,
        subject=subject_info,
        grades=[GradeResponse.model_validate(grade) for grade in grades],
        improvement=improvement,
    )


@router.get(
    "/students/{student_id}/subjects/{subject_id}/improvement", response_model=ImprovementResponse
)
async def get_improvement_analysis(
    student_id: int,
    subject_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get detailed improvement analysis for a student in a specific subject.

    Calculates improvement percentage and trends across terms.
    """
    grade_service = GradeService(db)
    improvement = grade_service.calculate_improvement(student_id, subject_id, current_user)

    if not improvement:
        # Check if student exists and is accessible
        if not grade_service.can_edit_student_grades(current_user, student_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Student not found or access denied"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Insufficient grade data for improvement analysis",
            )

    return ImprovementResponse(student_id=student_id, subject_id=subject_id, **improvement)


@router.get("/performance/stats", response_model=PerformanceStatsResponse)
async def get_performance_statistics(
    term_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get comprehensive performance statistics for accessible students.

    Includes performance band distribution, averages, and subject statistics.
    Useful for administrative reporting and analysis.
    """
    grade_service = GradeService(db)
    summary = grade_service.get_grade_summary(current_user, term_id)

    # Calculate performance statistics
    performance_bands = {"Outstanding": 0, "Good": 0, "Satisfactory": 0, "Needs Improvement": 0}
    all_scores = []
    subject_totals = {}
    subject_counts = {}

    for student_data in summary["students"]:
        if student_data["grades"]:
            # Calculate student average
            student_scores = [float(grade.score) for grade in student_data["grades"]]
            student_average = sum(student_scores) / len(student_scores)
            all_scores.append(student_average)

            # Count performance band
            performance_band = grade_service.calculate_performance_band(student_average)
            performance_bands[performance_band] += 1

            # Accumulate subject scores
            for grade in student_data["grades"]:
                subject_name = grade.subject.name
                if subject_name not in subject_totals:
                    subject_totals[subject_name] = 0
                    subject_counts[subject_name] = 0
                subject_totals[subject_name] += float(grade.score)
                subject_counts[subject_name] += 1

    # Calculate overall statistics
    overall_average = sum(all_scores) / len(all_scores) if all_scores else 0
    highest_score = max(all_scores) if all_scores else 0
    lowest_score = min(all_scores) if all_scores else 0

    # Calculate subject averages
    subject_averages = {}
    for subject_name in subject_totals:
        subject_averages[subject_name] = subject_totals[subject_name] / subject_counts[subject_name]

    return PerformanceStatsResponse(
        total_students=len([s for s in summary["students"] if s["grades"]]),
        performance_bands=performance_bands,
        average_score=overall_average,
        highest_score=highest_score,
        lowest_score=lowest_score,
        subject_averages=subject_averages,
    )


@router.get("/verify/{student_id}/edit-access")
async def verify_grade_edit_access(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Verify if current user can edit grades for a specific student.

    Returns access status and reason.
    Useful for UI permission checks.
    """
    grade_service = GradeService(db)
    can_edit = grade_service.can_edit_student_grades(current_user, student_id)

    return {
        "student_id": student_id,
        "can_edit_grades": can_edit,
        "user_role": current_user.role.value,
        "user_school_id": current_user.school_id,
        "reason": "Access granted"
        if can_edit
        else "Permission denied - check role and class assignments",
    }
