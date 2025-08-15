from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models import User
from app.schemas.class_schemas import (
    ClassDetailResponse,
    ClassResponse,
    ClassStudentResponse,
    ClassSummaryResponse,
    TeacherAssignmentResponse,
)
from app.schemas.student_schemas import StudentBaseResponse
from app.services.class_service import ClassService

router = APIRouter()


@router.get("/", response_model=List[ClassResponse])
async def list_classes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List classes accessible to the current user based on their role.

    - Form teachers: Only assigned classes
    - Year heads: All classes in their school
    - Admins: All classes in their school
    """
    class_service = ClassService(db)
    classes = class_service.get_accessible_classes(current_user)

    # Add student count to each class
    class_responses = []
    for class_obj in classes:
        class_response = ClassResponse.model_validate(class_obj)
        class_response.student_count = len(class_obj.students) if class_obj.students else 0
        class_responses.append(class_response)

    return class_responses


@router.get("/{class_id}", response_model=ClassDetailResponse)
async def get_class(
    class_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get detailed information about a specific class.

    Includes class details, students, and teacher assignments.
    Access controlled by user role and teacher assignments.
    """
    class_service = ClassService(db)
    class_obj = class_service.get_class_by_id(class_id, current_user)

    if not class_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Class not found or access denied"
        )

    return ClassDetailResponse.model_validate(class_obj)


@router.get("/{class_id}/students", response_model=ClassStudentResponse)
async def get_class_students(
    class_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all students in a specific class.

    Returns class information and student roster.
    Access controlled by teacher assignments.
    """
    class_service = ClassService(db)

    # Verify access to class first
    class_obj = class_service.get_class_by_id(class_id, current_user)
    if not class_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Class not found or access denied"
        )

    # Get students in the class
    students = class_service.get_class_students(class_id, current_user)

    return ClassStudentResponse(
        class_info=class_obj,
        students=[StudentBaseResponse.model_validate(student) for student in students],
        total_students=len(students),
    )


@router.get("/{class_id}/teachers", response_model=List[TeacherAssignmentResponse])
async def get_class_teachers(
    class_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get teacher assignments for a specific class.

    Only accessible to year heads and admins.
    Form teachers cannot see other teachers' assignments.
    """
    class_service = ClassService(db)
    assignments = class_service.get_teacher_assignments(class_id, current_user)

    if not assignments and not class_service.can_access_class(class_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Class not found or access denied"
        )

    return [TeacherAssignmentResponse.model_validate(assignment) for assignment in assignments]


@router.get("/summary/overview", response_model=List[ClassSummaryResponse])
async def get_classes_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get summary overview of all accessible classes.

    Includes basic info, student counts, and performance statistics.
    Useful for dashboard displays.
    """
    class_service = ClassService(db)
    classes = class_service.get_accessible_classes(current_user)

    summaries = []
    for class_obj in classes:
        total_students = len(class_obj.students) if class_obj.students else 0

        # Calculate class performance statistics
        average_class_score = None
        performance_distribution = {
            "Outstanding": 0,
            "Good": 0,
            "Satisfactory": 0,
            "Needs Improvement": 0,
        }

        if class_obj.students:
            student_averages = []

            for student in class_obj.students:
                if student.grades:
                    # Calculate student average
                    total_score = sum(float(grade.score) for grade in student.grades)
                    student_average = total_score / len(student.grades)
                    student_averages.append(student_average)

                    # Categorize performance
                    if student_average >= 85:
                        performance_distribution["Outstanding"] += 1
                    elif student_average >= 70:
                        performance_distribution["Good"] += 1
                    elif student_average >= 55:
                        performance_distribution["Satisfactory"] += 1
                    else:
                        performance_distribution["Needs Improvement"] += 1

            # Calculate class average
            if student_averages:
                average_class_score = sum(student_averages) / len(student_averages)

        summaries.append(
            ClassSummaryResponse(
                id=class_obj.id,
                name=class_obj.name,
                level=class_obj.level,
                section=class_obj.section,
                total_students=total_students,
                average_class_score=average_class_score,
                performance_distribution=performance_distribution,
            )
        )

    return summaries


@router.get("/accessible/ids")
async def get_accessible_class_ids(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get list of class IDs accessible to the current user.

    Utility endpoint for filtering other operations.
    """
    class_service = ClassService(db)
    class_ids = class_service.get_accessible_class_ids(current_user)

    return {
        "class_ids": class_ids,
        "total_count": len(class_ids),
        "user_role": current_user.role.value,
        "school_id": current_user.school_id,
    }


@router.get("/verify/{class_id}/access")
async def verify_class_access(
    class_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Verify if current user has access to a specific class.

    Returns access status and reason.
    Useful for UI permission checks.
    """
    class_service = ClassService(db)
    has_access = class_service.can_access_class(class_id, current_user)

    # Get class for additional context (if accessible)
    class_obj = None
    if has_access:
        class_obj = class_service.get_class_by_id(class_id, current_user)

    return {
        "class_id": class_id,
        "has_access": has_access,
        "user_role": current_user.role.value,
        "user_school_id": current_user.school_id,
        "class_info": {
            "name": class_obj.name if class_obj else None,
            "level": class_obj.level if class_obj else None,
            "section": class_obj.section if class_obj else None,
            "school_id": class_obj.school_id if class_obj else None,
            "student_count": len(class_obj.students) if class_obj and class_obj.students else 0,
        }
        if class_obj
        else None,
    }


@router.get("/teachers/{teacher_id}/verify/{class_id}")
async def verify_teacher_assignment(
    teacher_id: int,
    class_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Verify if a teacher is assigned to a specific class.

    Only accessible to:
    - The teacher themselves (for their own assignments)
    - Year heads and admins (for any assignments in their school)
    """
    class_service = ClassService(db)
    is_assigned = class_service.is_teacher_assigned_to_class(teacher_id, class_id, current_user)

    return {
        "teacher_id": teacher_id,
        "class_id": class_id,
        "is_assigned": is_assigned,
        "verified_by": current_user.username,
        "user_role": current_user.role.value,
    }
