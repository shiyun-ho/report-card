from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.models import Class, Student, TeacherClassAssignment, User, UserRole


class ClassService:
    """
    Service for managing class data with role-based access control.

    Implements teacher assignment-based access control:
    - Form teachers: Only assigned classes
    - Year heads: All classes in their school
    - Admins: All classes in their school
    """

    def __init__(self, db: Session):
        self.db = db

    def get_accessible_classes(self, user: User) -> List[Class]:
        """
        Get classes accessible to user based on role.

        Args:
            user: Current authenticated user

        Returns:
            List of classes accessible to the user
        """
        if user.role == UserRole.FORM_TEACHER:
            # Form teachers only see assigned classes
            return (
                self.db.query(Class)
                .join(TeacherClassAssignment)
                .filter(
                    TeacherClassAssignment.teacher_id == user.id, Class.school_id == user.school_id
                )
                .options(joinedload(Class.school), joinedload(Class.students))
                .all()
            )

        elif user.role in [UserRole.YEAR_HEAD, UserRole.ADMIN]:
            # Year heads and admins see all classes in their school
            return (
                self.db.query(Class)
                .filter(Class.school_id == user.school_id)
                .options(joinedload(Class.school), joinedload(Class.students))
                .all()
            )

        else:
            # Unknown role - return empty list for security
            return []

    def get_class_by_id(self, class_id: int, user: User) -> Optional[Class]:
        """
        Get a specific class by ID with access control.

        Args:
            class_id: ID of the class to retrieve
            user: Current authenticated user

        Returns:
            Class object if accessible, None otherwise
        """
        class_obj = (
            self.db.query(Class)
            .filter(Class.id == class_id)
            .options(
                joinedload(Class.school),
                joinedload(Class.students),
                joinedload(Class.teacher_assignments),
            )
            .first()
        )

        if not class_obj:
            return None

        # Check school isolation
        if class_obj.school_id != user.school_id:
            return None

        # Check role-based access
        if user.role == UserRole.FORM_TEACHER:
            # Check if teacher is assigned to this class
            assignment = (
                self.db.query(TeacherClassAssignment)
                .filter(
                    TeacherClassAssignment.teacher_id == user.id,
                    TeacherClassAssignment.class_id == class_id,
                )
                .first()
            )
            return class_obj if assignment else None

        elif user.role in [UserRole.YEAR_HEAD, UserRole.ADMIN]:
            return class_obj

        return None

    def get_class_students(self, class_id: int, user: User) -> List[Student]:
        """
        Get all students in a specific class with access control.

        Args:
            class_id: ID of the class
            user: Current authenticated user

        Returns:
            List of students in the class if accessible
        """
        # First verify access to the class
        if not self.can_access_class(class_id, user):
            return []

        return (
            self.db.query(Student)
            .filter(Student.class_id == class_id, Student.school_id == user.school_id)
            .options(joinedload(Student.class_obj), joinedload(Student.school))
            .all()
        )

    def can_access_class(self, class_id: int, user: User) -> bool:
        """
        Check if user can access a specific class.

        Args:
            class_id: ID of the class
            user: Current authenticated user

        Returns:
            True if user can access the class, False otherwise
        """
        class_obj = self.db.query(Class).filter(Class.id == class_id).first()

        if not class_obj:
            return False

        # Check school isolation
        if class_obj.school_id != user.school_id:
            return False

        # Check role-based access
        if user.role == UserRole.FORM_TEACHER:
            assignment = (
                self.db.query(TeacherClassAssignment)
                .filter(
                    TeacherClassAssignment.teacher_id == user.id,
                    TeacherClassAssignment.class_id == class_id,
                )
                .first()
            )
            return assignment is not None

        elif user.role in [UserRole.YEAR_HEAD, UserRole.ADMIN]:
            return True

        return False

    def get_accessible_class_ids(self, user: User) -> List[int]:
        """
        Get list of class IDs accessible to the user.

        Useful for filtering other queries.

        Args:
            user: Current authenticated user

        Returns:
            List of accessible class IDs
        """
        if user.role == UserRole.FORM_TEACHER:
            # Get assigned class IDs only
            class_ids = (
                self.db.query(TeacherClassAssignment.class_id)
                .join(Class)
                .filter(
                    TeacherClassAssignment.teacher_id == user.id, Class.school_id == user.school_id
                )
                .all()
            )
            return [class_id[0] for class_id in class_ids]

        elif user.role in [UserRole.YEAR_HEAD, UserRole.ADMIN]:
            # All classes in school
            class_ids = self.db.query(Class.id).filter(Class.school_id == user.school_id).all()
            return [class_id[0] for class_id in class_ids]

        return []

    def get_teacher_assignments(self, class_id: int, user: User) -> List[TeacherClassAssignment]:
        """
        Get teacher assignments for a class.

        Only accessible to year heads and admins.

        Args:
            class_id: ID of the class
            user: Current authenticated user

        Returns:
            List of teacher assignments if accessible
        """
        # Only year heads and admins can see teacher assignments
        if user.role not in [UserRole.YEAR_HEAD, UserRole.ADMIN]:
            return []

        # Verify class access first
        if not self.can_access_class(class_id, user):
            return []

        return (
            self.db.query(TeacherClassAssignment)
            .filter(TeacherClassAssignment.class_id == class_id)
            .options(joinedload(TeacherClassAssignment.teacher))
            .all()
        )

    def is_teacher_assigned_to_class(self, teacher_id: int, class_id: int, user: User) -> bool:
        """
        Check if a teacher is assigned to a specific class.

        Only accessible to year heads and admins, or the teacher themselves.

        Args:
            teacher_id: ID of the teacher to check
            class_id: ID of the class
            user: Current authenticated user

        Returns:
            True if teacher is assigned, False otherwise
        """
        # Teachers can check their own assignments
        # Year heads and admins can check any assignments in their school
        if user.role == UserRole.FORM_TEACHER and user.id != teacher_id:
            return False

        if user.role not in [UserRole.FORM_TEACHER, UserRole.YEAR_HEAD, UserRole.ADMIN]:
            return False

        # Verify class access first
        if not self.can_access_class(class_id, user):
            return False

        assignment = (
            self.db.query(TeacherClassAssignment)
            .filter(
                TeacherClassAssignment.teacher_id == teacher_id,
                TeacherClassAssignment.class_id == class_id,
            )
            .first()
        )

        return assignment is not None
