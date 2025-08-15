from decimal import Decimal
from typing import Dict, List, Optional

from sqlalchemy.orm import Session, joinedload

from app.models import Grade, Student, TeacherClassAssignment, Term, User, UserRole


class GradeService:
    """
    Service for managing grade data with role-based access control.

    Implements permission-based grade editing:
    - Form teachers: Can edit grades for assigned students only
    - Year heads: Can edit grades for all students in their school
    - Admins: Can edit grades for all students in their school
    """

    def __init__(self, db: Session):
        self.db = db

    def can_edit_student_grades(self, user: User, student_id: int) -> bool:
        """
        Check if user can edit grades for specific student.

        Args:
            user: Current authenticated user
            student_id: ID of the student

        Returns:
            True if user can edit grades, False otherwise
        """
        student = self.db.query(Student).filter(Student.id == student_id).first()
        if not student or student.school_id != user.school_id:
            return False

        if user.role == UserRole.FORM_TEACHER:
            # Check if teacher is assigned to student's class
            assignment = (
                self.db.query(TeacherClassAssignment)
                .filter(
                    TeacherClassAssignment.teacher_id == user.id,
                    TeacherClassAssignment.class_id == student.class_id,
                )
                .first()
            )
            return assignment is not None

        elif user.role in [UserRole.YEAR_HEAD, UserRole.ADMIN]:
            return True

        return False

    def get_student_grades(
        self, student_id: int, term_id: Optional[int], user: User
    ) -> List[Grade]:
        """
        Get grades for a specific student and term.

        Args:
            student_id: ID of the student
            term_id: ID of the term (optional, gets all terms if None)
            user: Current authenticated user

        Returns:
            List of grades if accessible, empty list otherwise
        """
        # Check access permission
        if not self.can_edit_student_grades(user, student_id):
            return []

        query = (
            self.db.query(Grade)
            .filter(Grade.student_id == student_id)
            .options(joinedload(Grade.subject), joinedload(Grade.term), joinedload(Grade.student))
        )

        if term_id:
            query = query.filter(Grade.term_id == term_id)

        return query.all()

    def update_student_grades(
        self, student_id: int, term_id: int, grades_data: Dict[int, Decimal], user: User
    ) -> Dict[str, any]:
        """
        Update grades for a student in a specific term.

        Args:
            student_id: ID of the student
            term_id: ID of the term
            grades_data: Dictionary mapping subject_id to score
            user: Current authenticated user

        Returns:
            Dictionary with success status and updated grades
        """
        # Check permission
        if not self.can_edit_student_grades(user, student_id):
            return {"success": False, "error": "Permission denied"}

        # Verify student and term exist and belong to user's school
        student = self.db.query(Student).filter(Student.id == student_id).first()
        if not student or student.school_id != user.school_id:
            return {"success": False, "error": "Student not found"}

        term = self.db.query(Term).filter(Term.id == term_id).first()
        if not term or term.school_id != user.school_id:
            return {"success": False, "error": "Term not found"}

        updated_grades = []

        try:
            for subject_id, score in grades_data.items():
                # Validate score range
                if not (0 <= score <= 100):
                    return {
                        "success": False,
                        "error": f"Invalid score {score} for subject {subject_id}. Must be between 0 and 100.",
                    }

                # Find existing grade or create new one
                grade = (
                    self.db.query(Grade)
                    .filter(
                        Grade.student_id == student_id,
                        Grade.term_id == term_id,
                        Grade.subject_id == subject_id,
                    )
                    .first()
                )

                if grade:
                    # Update existing grade
                    grade.score = score
                    grade.modified_by_id = user.id
                else:
                    # Create new grade
                    grade = Grade(
                        student_id=student_id,
                        term_id=term_id,
                        subject_id=subject_id,
                        score=score,
                        modified_by_id=user.id,
                    )
                    self.db.add(grade)

                updated_grades.append(grade)

            # Commit all changes
            self.db.commit()

            # Refresh grades to get updated relationships
            for grade in updated_grades:
                self.db.refresh(grade)

            return {
                "success": True,
                "grades": updated_grades,
                "message": f"Updated {len(updated_grades)} grades for student {student_id}",
            }

        except Exception as e:
            self.db.rollback()
            return {"success": False, "error": f"Database error: {str(e)}"}

    def get_grade_summary(self, user: User, term_id: Optional[int] = None) -> Dict[str, any]:
        """
        Get grade summary for students accessible to the user.

        Args:
            user: Current authenticated user
            term_id: Optional term ID to filter by

        Returns:
            Dictionary with grade statistics and summaries
        """
        # Get accessible student IDs
        from app.services.student_service import StudentService

        student_service = StudentService(self.db)
        accessible_student_ids = student_service.get_accessible_student_ids(user)

        if not accessible_student_ids:
            return {"students": [], "total_students": 0}

        # Build base query
        query = (
            self.db.query(Grade)
            .filter(Grade.student_id.in_(accessible_student_ids))
            .options(joinedload(Grade.student), joinedload(Grade.subject), joinedload(Grade.term))
        )

        if term_id:
            query = query.filter(Grade.term_id == term_id)

        grades = query.all()

        # Group grades by student
        student_summaries = {}
        for grade in grades:
            student_id = grade.student_id
            if student_id not in student_summaries:
                student_summaries[student_id] = {
                    "student_id": student_id,
                    "student_name": grade.student.full_name,
                    "class_name": grade.student.class_obj.name,
                    "grades": [],
                    "average": 0,
                    "total_subjects": 0,
                }
            student_summaries[student_id]["grades"].append(grade)

        # Calculate averages
        for student_id, summary in student_summaries.items():
            if summary["grades"]:
                total_score = sum(float(grade.score) for grade in summary["grades"])
                summary["average"] = total_score / len(summary["grades"])
                summary["total_subjects"] = len(summary["grades"])

        return {
            "students": list(student_summaries.values()),
            "total_students": len(student_summaries),
            "total_grades": len(grades),
        }

    def calculate_performance_band(self, average_score: float) -> str:
        """
        Calculate performance band based on average score.

        Args:
            average_score: Average score across subjects

        Returns:
            Performance band string
        """
        if average_score >= 85:
            return "Outstanding"
        elif average_score >= 70:
            return "Good"
        elif average_score >= 55:
            return "Satisfactory"
        else:
            return "Needs Improvement"

    def get_grade_history(self, student_id: int, subject_id: int, user: User) -> List[Grade]:
        """
        Get grade history for a student in a specific subject.

        Args:
            student_id: ID of the student
            subject_id: ID of the subject
            user: Current authenticated user

        Returns:
            List of grades ordered by term
        """
        # Check access permission
        if not self.can_edit_student_grades(user, student_id):
            return []

        return (
            self.db.query(Grade)
            .filter(Grade.student_id == student_id, Grade.subject_id == subject_id)
            .join(Term)
            .order_by(Term.term_number)
            .options(
                joinedload(Grade.term), joinedload(Grade.subject), joinedload(Grade.modified_by)
            )
            .all()
        )

    def calculate_improvement(
        self, student_id: int, subject_id: int, user: User
    ) -> Optional[Dict[str, any]]:
        """
        Calculate grade improvement for a student in a specific subject.

        Args:
            student_id: ID of the student
            subject_id: ID of the subject
            user: Current authenticated user

        Returns:
            Dictionary with improvement statistics or None if insufficient data
        """
        grades = self.get_grade_history(student_id, subject_id, user)

        if len(grades) < 2:
            return None

        # Sort by term number
        grades.sort(key=lambda g: g.term.term_number)

        first_grade = grades[0]
        latest_grade = grades[-1]

        improvement_amount = float(latest_grade.score) - float(first_grade.score)
        improvement_percentage = (improvement_amount / float(first_grade.score)) * 100

        return {
            "first_score": float(first_grade.score),
            "latest_score": float(latest_grade.score),
            "improvement_amount": improvement_amount,
            "improvement_percentage": improvement_percentage,
            "total_terms": len(grades),
            "first_term": first_grade.term.name,
            "latest_term": latest_grade.term.name,
        }
