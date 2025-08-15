from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.models import Student, TeacherClassAssignment, User, UserRole


class StudentService:
    """
    Service for managing student data with role-based access control.

    Implements multi-tenant isolation and role-based filtering:
    - Form teachers: Only assigned students
    - Year heads: All students in their school
    - Admins: All students in their school
    """

    def __init__(self, db: Session):
        self.db = db

    def get_students_for_user(self, user: User) -> List[Student]:
        """
        Get students based on user role and assignments.

        Args:
            user: Current authenticated user

        Returns:
            List of students accessible to the user
        """
        # Base query with school isolation and eager loading
        base_query = (
            self.db.query(Student)
            .filter(Student.school_id == user.school_id)
            .options(joinedload(Student.class_obj), joinedload(Student.school))
        )

        if user.role == UserRole.FORM_TEACHER:
            # Form teachers only see students in their assigned classes
            assigned_class_ids = (
                self.db.query(TeacherClassAssignment.class_id)
                .filter(TeacherClassAssignment.teacher_id == user.id)
                .subquery()
            )
            return base_query.filter(Student.class_id.in_(assigned_class_ids)).all()

        elif user.role in [UserRole.YEAR_HEAD, UserRole.ADMIN]:
            # Year heads and admins see all students in their school
            return base_query.all()

        else:
            # Unknown role - return empty list for security
            return []

    def get_student_by_id(self, student_id: int, user: User) -> Optional[Student]:
        """
        Get a specific student by ID with access control.

        Args:
            student_id: ID of the student to retrieve
            user: Current authenticated user

        Returns:
            Student object if accessible, None otherwise
        """
        student = (
            self.db.query(Student)
            .filter(Student.id == student_id)
            .options(
                joinedload(Student.class_obj),
                joinedload(Student.school),
                joinedload(Student.grades),
            )
            .first()
        )

        if not student:
            return None

        # Check school isolation
        if student.school_id != user.school_id:
            return None

        # Check role-based access
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
            return student if assignment else None

        elif user.role in [UserRole.YEAR_HEAD, UserRole.ADMIN]:
            return student

        return None

    def get_students_in_class(self, class_id: int, user: User) -> List[Student]:
        """
        Get all students in a specific class with access control.

        Args:
            class_id: ID of the class
            user: Current authenticated user

        Returns:
            List of students in the class if accessible
        """
        # First check if user has access to this class
        if user.role == UserRole.FORM_TEACHER:
            assignment = (
                self.db.query(TeacherClassAssignment)
                .filter(
                    TeacherClassAssignment.teacher_id == user.id,
                    TeacherClassAssignment.class_id == class_id,
                )
                .first()
            )
            if not assignment:
                return []

        # Get students with school isolation
        students = (
            self.db.query(Student)
            .filter(Student.class_id == class_id, Student.school_id == user.school_id)
            .options(joinedload(Student.class_obj), joinedload(Student.school))
            .all()
        )

        return students

    def can_access_student(self, student_id: int, user: User) -> bool:
        """
        Check if user can access a specific student.

        Args:
            student_id: ID of the student
            user: Current authenticated user

        Returns:
            True if user can access the student, False otherwise
        """
        student = self.get_student_by_id(student_id, user)
        return student is not None

    def get_accessible_student_ids(self, user: User) -> List[int]:
        """
        Get list of student IDs accessible to the user.

        Useful for filtering other queries.

        Args:
            user: Current authenticated user

        Returns:
            List of accessible student IDs
        """
        if user.role == UserRole.FORM_TEACHER:
            # Get students in assigned classes only
            assigned_class_ids = (
                self.db.query(TeacherClassAssignment.class_id)
                .filter(TeacherClassAssignment.teacher_id == user.id)
                .subquery()
            )
            student_ids = (
                self.db.query(Student.id)
                .filter(
                    Student.school_id == user.school_id, Student.class_id.in_(assigned_class_ids)
                )
                .all()
            )
            return [student_id[0] for student_id in student_ids]

        elif user.role in [UserRole.YEAR_HEAD, UserRole.ADMIN]:
            # All students in school
            student_ids = (
                self.db.query(Student.id).filter(Student.school_id == user.school_id).all()
            )
            return [student_id[0] for student_id in student_ids]

        return []
