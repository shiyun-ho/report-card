from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models import User
from app.schemas.student_schemas import (
    StudentDetailResponse,
    StudentResponse,
    StudentSummaryResponse,
)
from app.services.student_service import StudentService

router = APIRouter()


@router.get("/", response_model=List[StudentResponse])
async def list_students(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List students accessible to the current user based on their role.

    - Form teachers: Only assigned students
    - Year heads: All students in their school
    - Admins: All students in their school
    """
    student_service = StudentService(db)
    students = student_service.get_students_for_user(current_user)

    return [StudentResponse.model_validate(student) for student in students]


@router.get("/{student_id}", response_model=StudentDetailResponse)
async def get_student(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get detailed information about a specific student.

    Includes student details and grade history.
    Access controlled by user role and teacher assignments.
    """
    student_service = StudentService(db)
    student = student_service.get_student_by_id(student_id, current_user)

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student not found or access denied"
        )

    return StudentDetailResponse.model_validate(student)


@router.get("/summary/overview", response_model=List[StudentSummaryResponse])
async def get_students_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get summary overview of all accessible students.

    Includes basic info, grade counts, and performance indicators.
    Useful for dashboard displays.
    """
    student_service = StudentService(db)
    students = student_service.get_students_for_user(current_user)

    # Calculate summary data for each student
    summaries = []
    for student in students:
        # Calculate basic statistics
        total_grades = len(student.grades) if student.grades else 0

        average_score = None
        performance_band = None
        latest_term = None

        if student.grades:
            # Calculate average score
            total_score = sum(float(grade.score) for grade in student.grades)
            average_score = total_score / total_grades

            # Determine performance band
            if average_score >= 85:
                performance_band = "Outstanding"
            elif average_score >= 70:
                performance_band = "Good"
            elif average_score >= 55:
                performance_band = "Satisfactory"
            else:
                performance_band = "Needs Improvement"

            # Get latest term
            latest_grade = max(student.grades, key=lambda g: g.term.term_number)
            latest_term = latest_grade.term.name

        summaries.append(
            StudentSummaryResponse(
                id=student.id,
                student_id=student.student_id,
                full_name=student.full_name,
                class_name=student.class_obj.name,
                total_grades=total_grades,
                average_score=average_score,
                performance_band=performance_band,
                latest_term=latest_term,
            )
        )

    return summaries


@router.get("/class/{class_id}/students", response_model=List[StudentResponse])
async def get_students_in_class(
    class_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all students in a specific class.

    Access controlled by teacher assignments:
    - Form teachers: Only their assigned classes
    - Year heads: All classes in their school
    """
    student_service = StudentService(db)
    students = student_service.get_students_in_class(class_id, current_user)

    return [StudentResponse.model_validate(student) for student in students]


@router.get("/accessible/ids")
async def get_accessible_student_ids(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get list of student IDs accessible to the current user.

    Utility endpoint for filtering other operations.
    """
    student_service = StudentService(db)
    student_ids = student_service.get_accessible_student_ids(current_user)

    return {
        "student_ids": student_ids,
        "total_count": len(student_ids),
        "user_role": current_user.role.value,
        "school_id": current_user.school_id,
    }


@router.get("/verify/{student_id}/access")
async def verify_student_access(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Verify if current user has access to a specific student.

    Returns access status and reason.
    Useful for UI permission checks.
    """
    student_service = StudentService(db)
    has_access = student_service.can_access_student(student_id, current_user)

    # Get student for additional context (if accessible)
    student = None
    if has_access:
        student = student_service.get_student_by_id(student_id, current_user)

    return {
        "student_id": student_id,
        "has_access": has_access,
        "user_role": current_user.role.value,
        "user_school_id": current_user.school_id,
        "student_info": {
            "name": student.full_name if student else None,
            "class": student.class_obj.name if student else None,
            "school_id": student.school_id if student else None,
        }
        if student
        else None,
    }
