from app.models import (
    Achievement,
    AchievementCategory,
    Class,
    Grade,
    ReportCard,
    ReportComponent,
    School,
    Student,
    Subject,
    TeacherClassAssignment,
    Term,
    User,
)


def test_all_models_imported():
    """Test that all models are properly imported."""
    assert School.__tablename__ == "schools"
    assert User.__tablename__ == "users"
    assert Class.__tablename__ == "classes"
    assert Student.__tablename__ == "students"
    assert Term.__tablename__ == "terms"
    assert Subject.__tablename__ == "subjects"
    assert Grade.__tablename__ == "grades"
    assert AchievementCategory.__tablename__ == "achievement_categories"
    assert Achievement.__tablename__ == "achievements"
    assert ReportCard.__tablename__ == "report_cards"
    assert ReportComponent.__tablename__ == "report_components"
    assert TeacherClassAssignment.__tablename__ == "teacher_class_assignments"


def test_relationships():
    """Test that relationships are properly defined."""
    # Test School relationships
    assert hasattr(School, "users")
    assert hasattr(School, "classes")
    assert hasattr(School, "students")
    assert hasattr(School, "terms")

    # Test User relationships
    assert hasattr(User, "school")
    assert hasattr(User, "class_assignments")

    # Test Student relationships
    assert hasattr(Student, "school")
    assert hasattr(Student, "class_obj")
    assert hasattr(Student, "grades")
    assert hasattr(Student, "report_cards")


def test_multi_tenant_fields():
    """Test that all relevant models have school_id for multi-tenancy."""
    models_with_school_id = [User, Class, Student, Term]
    for model in models_with_school_id:
        columns = [c.name for c in model.__table__.columns]
        assert "school_id" in columns, f"{model.__name__} missing school_id"


def test_unique_constraints():
    """Test that unique constraints are properly defined."""
    # Check Student unique constraint
    student_constraints = [c.name for c in Student.__table__.constraints]
    assert "_student_school_uc" in student_constraints

    # Check Grade unique constraint
    grade_constraints = [c.name for c in Grade.__table__.constraints]
    assert "_student_term_subject_uc" in grade_constraints
