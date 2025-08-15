"""Tests for achievement suggestion functionality."""
import os
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.seed_data import seed_database
from app.models import (
    AchievementCategory, Grade, Student, Subject, Term, User, UserRole, School, Class
)
from app.services.achievement_service import AchievementService

# Security-compliant credential management - ONLY from environment
TEST_PASSWORD = os.getenv("SEED_DEFAULT_PASSWORD")
if not TEST_PASSWORD:
    pytest.skip("SEED_DEFAULT_PASSWORD environment variable not set", allow_module_level=True)


class TestAchievementService:
    """Test cases for AchievementService class."""

    def test_achievement_service_initialization(self, db_session):
        """Test AchievementService can be initialized properly."""
        service = AchievementService(db_session)
        assert service.db == db_session
        assert service.grade_service is not None

    def test_can_access_student_achievements_form_teacher_assigned(self, db_session):
        """Test form teacher can access achievements for assigned students."""
        with patch('app.core.seed_data.SessionLocal', return_value=db_session):
            seed_database()

        service = AchievementService(db_session)
        
        # Get first student and their form teacher
        student = db_session.query(Student).first()
        form_teacher = db_session.query(User).filter(
            User.role == UserRole.FORM_TEACHER,
            User.school_id == student.school_id
        ).first()

        assert service.can_access_student_achievements(form_teacher, student.id)

    def test_can_access_student_achievements_year_head(self, db_session):
        """Test year head can access achievements for all students in school."""
        with patch('app.core.seed_data.SessionLocal', return_value=db_session):
            seed_database()

        service = AchievementService(db_session)
        
        # Get any student and a year head from same school
        student = db_session.query(Student).first()
        year_head = db_session.query(User).filter(
            User.role == UserRole.YEAR_HEAD,
            User.school_id == student.school_id
        ).first()

        assert service.can_access_student_achievements(year_head, student.id)

    def test_can_access_student_achievements_different_school(self, db_session):
        """Test teacher cannot access achievements for students from different school."""
        with patch('app.core.seed_data.SessionLocal', return_value=db_session):
            seed_database()

        service = AchievementService(db_session)
        
        # Get student from one school and teacher from another
        schools = db_session.query(School).all()
        assert len(schools) >= 2, "Need at least 2 schools for this test"
        
        student_school1 = db_session.query(Student).filter(
            Student.school_id == schools[0].id
        ).first()
        teacher_school2 = db_session.query(User).filter(
            User.school_id == schools[1].id
        ).first()

        assert not service.can_access_student_achievements(teacher_school2, student_school1.id)

    def test_get_achievement_suggestions_significant_improvement_pattern(self, db_session):
        """Test achievement suggestions for significant improvement pattern students."""
        with patch('app.core.seed_data.SessionLocal', return_value=db_session):
            seed_database()

        service = AchievementService(db_session)
        
        # Get first student (should have significant improvement pattern)
        students = db_session.query(Student).order_by(Student.id).all()
        sig_improvement_student = students[0]
        
        # Get a teacher from same school
        teacher = db_session.query(User).filter(
            User.school_id == sig_improvement_student.school_id,
            User.role == UserRole.FORM_TEACHER
        ).first()
        
        # Get term 3 (final term)
        term3 = db_session.query(Term).filter(
            Term.school_id == sig_improvement_student.school_id,
            Term.term_number == 3
        ).first()

        suggestions = service.get_achievement_suggestions(
            sig_improvement_student.id, term3.id, teacher
        )

        assert suggestions is not None
        assert suggestions["student_id"] == sig_improvement_student.id
        assert suggestions["term_id"] == term3.id
        assert len(suggestions["suggestions"]) > 0
        
        # Should find significant improvement achievements
        suggestion_titles = [s["title"] for s in suggestions["suggestions"]]
        assert any("significant improvement" in title.lower() for title in suggestion_titles)

    def test_get_achievement_suggestions_excellence_pattern(self, db_session):
        """Test achievement suggestions for excellence achiever pattern students."""
        with patch('app.core.seed_data.SessionLocal', return_value=db_session):
            seed_database()

        service = AchievementService(db_session)
        
        # Get excellence student (students 6-8)
        students = db_session.query(Student).order_by(Student.id).all()
        excellence_student = students[6]
        
        teacher = db_session.query(User).filter(
            User.school_id == excellence_student.school_id,
            User.role == UserRole.YEAR_HEAD
        ).first()
        
        term3 = db_session.query(Term).filter(
            Term.school_id == excellence_student.school_id,
            Term.term_number == 3
        ).first()

        suggestions = service.get_achievement_suggestions(
            excellence_student.id, term3.id, teacher
        )

        assert suggestions is not None
        assert len(suggestions["suggestions"]) > 0
        
        # Should find excellence achievements
        suggestion_titles = [s["title"] for s in suggestions["suggestions"]]
        assert any("excellence" in title.lower() for title in suggestion_titles)

    def test_get_achievement_suggestions_no_access(self, db_session):
        """Test that suggestions return None when user has no access."""
        with patch('app.core.seed_data.SessionLocal', return_value=db_session):
            seed_database()

        service = AchievementService(db_session)
        
        # Get student and teacher from different schools
        schools = db_session.query(School).all()
        student_school1 = db_session.query(Student).filter(
            Student.school_id == schools[0].id
        ).first()
        teacher_school2 = db_session.query(User).filter(
            User.school_id == schools[1].id
        ).first()
        
        term = db_session.query(Term).filter(
            Term.school_id == student_school1.school_id
        ).first()

        suggestions = service.get_achievement_suggestions(
            student_school1.id, term.id, teacher_school2
        )

        assert suggestions is None

    def test_subject_specific_suggestion_matching(self, db_session):
        """Test that subject-specific achievement matching works correctly."""
        with patch('app.core.seed_data.SessionLocal', return_value=db_session):
            seed_database()

        service = AchievementService(db_session)
        
        # Get subjects and achievement categories
        subjects = db_session.query(Subject).all()
        achievement_categories = db_session.query(AchievementCategory).all()
        
        # Get a student with improvement pattern
        student = db_session.query(Student).order_by(Student.id).first()
        teacher = db_session.query(User).filter(
            User.school_id == student.school_id
        ).first()
        
        term3 = db_session.query(Term).filter(
            Term.school_id == student.school_id,
            Term.term_number == 3
        ).first()

        suggestions = service._get_subject_specific_suggestions(
            student.id, term3.id, subjects, achievement_categories, teacher
        )

        assert isinstance(suggestions, list)
        # Should have suggestions for subjects with significant improvement
        assert len(suggestions) > 0
        
        # Verify suggestion structure
        for suggestion in suggestions:
            assert "title" in suggestion
            assert "description" in suggestion
            assert "category_name" in suggestion
            assert "relevance_score" in suggestion
            assert "explanation" in suggestion
            assert "supporting_data" in suggestion
            assert 0.0 <= suggestion["relevance_score"] <= 1.0

    def test_overall_achievement_suggestions(self, db_session):
        """Test overall achievement suggestions based on cross-subject performance."""
        with patch('app.core.seed_data.SessionLocal', return_value=db_session):
            seed_database()

        service = AchievementService(db_session)
        
        subjects = db_session.query(Subject).all()
        achievement_categories = db_session.query(AchievementCategory).all()
        
        # Get a student with consistent high performance
        student = db_session.query(Student).order_by(Student.id).all()[6]  # Excellence student
        teacher = db_session.query(User).filter(
            User.school_id == student.school_id
        ).first()
        
        term3 = db_session.query(Term).filter(
            Term.school_id == student.school_id,
            Term.term_number == 3
        ).first()

        suggestions = service._get_overall_achievement_suggestions(
            student.id, term3.id, subjects, achievement_categories, teacher
        )

        assert isinstance(suggestions, list)
        # Excellence students should trigger overall achievements
        # Note: This may be empty if no "overall" achievement categories exist
        
    def test_relevance_score_calculation_improvement(self, db_session):
        """Test relevance score calculation for improvement-based achievements."""
        service = AchievementService(db_session)
        
        # Test high improvement
        score_high = service._calculate_improvement_relevance_score(25.0, 20.0, 3)
        assert score_high >= 0.8
        
        # Test moderate improvement
        score_moderate = service._calculate_improvement_relevance_score(18.0, 20.0, 3)
        assert 0.5 <= score_moderate < 0.8
        
        # Test low improvement
        score_low = service._calculate_improvement_relevance_score(12.0, 20.0, 3)
        assert 0.0 < score_low < 0.5

    def test_relevance_score_calculation_score_based(self, db_session):
        """Test relevance score calculation for score-based achievements."""
        service = AchievementService(db_session)
        
        # Test exceptional performance
        score_exceptional = service._calculate_score_relevance_score(95.0, 90.0)
        assert score_exceptional >= 0.9
        
        # Test strong performance
        score_strong = service._calculate_score_relevance_score(92.0, 90.0)
        assert 0.8 <= score_strong < 0.95
        
        # Test below threshold
        score_below = service._calculate_score_relevance_score(88.0, 90.0)
        assert score_below == 0.0


class TestAchievementEndpoints:
    """Test cases for achievement API endpoints."""

    def test_suggest_achievements_success(self, test_client: TestClient, db_session):
        """Test successful achievement suggestion request."""
        with patch('app.core.seed_data.SessionLocal', return_value=db_session):
            seed_database()

        # Get a teacher and student
        student = db_session.query(Student).order_by(Student.id).first()
        teacher = db_session.query(User).filter(
            User.school_id == student.school_id,
            User.role == UserRole.FORM_TEACHER
        ).first()
        
        term3 = db_session.query(Term).filter(
            Term.school_id == student.school_id,
            Term.term_number == 3
        ).first()

        # Login as teacher
        login_response = test_client.post(
            f"{settings.API_V1_STR}/auth/login",
            json={
                "email": teacher.email,
                "password": TEST_PASSWORD,
            },
        )
        assert login_response.status_code == 200

        # Request achievement suggestions
        response = test_client.get(
            f"{settings.API_V1_STR}/achievements/suggest/{student.id}/{term3.id}"
        )

        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "student_id" in data
        assert "term_id" in data
        assert "student_name" in data
        assert "term_name" in data
        assert "suggestions" in data
        assert "total_suggestions" in data
        assert "average_relevance" in data
        
        assert data["student_id"] == student.id
        assert data["term_id"] == term3.id
        assert isinstance(data["suggestions"], list)
        assert isinstance(data["total_suggestions"], int)
        assert isinstance(data["average_relevance"], float)

    def test_suggest_achievements_unauthorized(self, test_client: TestClient, db_session):
        """Test achievement suggestion request without authentication."""
        with patch('app.core.seed_data.SessionLocal', return_value=db_session):
            seed_database()

        student = db_session.query(Student).first()
        term = db_session.query(Term).filter(
            Term.school_id == student.school_id
        ).first()

        response = test_client.get(
            f"{settings.API_V1_STR}/achievements/suggest/{student.id}/{term.id}"
        )

        assert response.status_code == 401

    def test_suggest_achievements_no_access_to_student(self, test_client: TestClient, db_session):
        """Test achievement suggestion request for student user has no access to."""
        with patch('app.core.seed_data.SessionLocal', return_value=db_session):
            seed_database()

        # Get student from one school and teacher from another
        schools = db_session.query(School).all()
        student_school1 = db_session.query(Student).filter(
            Student.school_id == schools[0].id
        ).first()
        teacher_school2 = db_session.query(User).filter(
            User.school_id == schools[1].id
        ).first()
        
        term = db_session.query(Term).filter(
            Term.school_id == student_school1.school_id
        ).first()

        # Login as teacher from different school
        login_response = test_client.post(
            f"{settings.API_V1_STR}/auth/login",
            json={
                "email": teacher_school2.email,
                "password": TEST_PASSWORD,
            },
        )
        assert login_response.status_code == 200

        # Request achievement suggestions
        response = test_client.get(
            f"{settings.API_V1_STR}/achievements/suggest/{student_school1.id}/{term.id}"
        )

        assert response.status_code == 404
        data = response.json()
        assert "Student not found or insufficient data for suggestions" in data["detail"]

    def test_suggest_achievements_invalid_student_id(self, test_client: TestClient, db_session):
        """Test achievement suggestion request with invalid student ID."""
        with patch('app.core.seed_data.SessionLocal', return_value=db_session):
            seed_database()

        teacher = db_session.query(User).filter(
            User.role == UserRole.FORM_TEACHER
        ).first()
        term = db_session.query(Term).filter(
            Term.school_id == teacher.school_id
        ).first()

        # Login as teacher
        login_response = test_client.post(
            f"{settings.API_V1_STR}/auth/login",
            json={
                "email": teacher.email,
                "password": TEST_PASSWORD,
            },
        )
        assert login_response.status_code == 200

        # Request with invalid student ID
        response = test_client.get(
            f"{settings.API_V1_STR}/achievements/suggest/99999/{term.id}"
        )

        assert response.status_code == 404

    def test_suggest_achievements_invalid_term_id(self, test_client: TestClient, db_session):
        """Test achievement suggestion request with invalid term ID."""
        with patch('app.core.seed_data.SessionLocal', return_value=db_session):
            seed_database()

        student = db_session.query(Student).first()
        teacher = db_session.query(User).filter(
            User.school_id == student.school_id,
            User.role == UserRole.FORM_TEACHER
        ).first()

        # Login as teacher
        login_response = test_client.post(
            f"{settings.API_V1_STR}/auth/login",
            json={
                "email": teacher.email,
                "password": TEST_PASSWORD,
            },
        )
        assert login_response.status_code == 200

        # Request with invalid term ID
        response = test_client.get(
            f"{settings.API_V1_STR}/achievements/suggest/{student.id}/99999"
        )

        assert response.status_code == 404

    def test_suggest_achievements_year_head_access(self, test_client: TestClient, db_session):
        """Test that year heads can access achievement suggestions for all students in school."""
        with patch('app.core.seed_data.SessionLocal', return_value=db_session):
            seed_database()

        # Get any student and year head from same school
        student = db_session.query(Student).first()
        year_head = db_session.query(User).filter(
            User.school_id == student.school_id,
            User.role == UserRole.YEAR_HEAD
        ).first()
        
        term = db_session.query(Term).filter(
            Term.school_id == student.school_id
        ).first()

        # Login as year head
        login_response = test_client.post(
            f"{settings.API_V1_STR}/auth/login",
            json={
                "email": year_head.email,
                "password": TEST_PASSWORD,
            },
        )
        assert login_response.status_code == 200

        # Request achievement suggestions
        response = test_client.get(
            f"{settings.API_V1_STR}/achievements/suggest/{student.id}/{term.id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["student_id"] == student.id

    def test_suggest_achievements_response_format_validation(self, test_client: TestClient, db_session):
        """Test that achievement suggestions response matches expected schema."""
        with patch('app.core.seed_data.SessionLocal', return_value=db_session):
            seed_database()

        # Get significant improvement student for predictable results
        students = db_session.query(Student).order_by(Student.id).all()
        sig_student = students[0]
        
        teacher = db_session.query(User).filter(
            User.school_id == sig_student.school_id,
            User.role == UserRole.FORM_TEACHER
        ).first()
        
        term3 = db_session.query(Term).filter(
            Term.school_id == sig_student.school_id,
            Term.term_number == 3
        ).first()

        # Login
        login_response = test_client.post(
            f"{settings.API_V1_STR}/auth/login",
            json={
                "email": teacher.email,
                "password": TEST_PASSWORD,
            },
        )
        assert login_response.status_code == 200

        # Get suggestions
        response = test_client.get(
            f"{settings.API_V1_STR}/achievements/suggest/{sig_student.id}/{term3.id}"
        )

        assert response.status_code == 200
        data = response.json()
        
        # Validate main response structure
        required_fields = ["student_id", "term_id", "student_name", "term_name", 
                          "suggestions", "total_suggestions", "average_relevance"]
        for field in required_fields:
            assert field in data
        
        # Validate suggestions array structure
        for suggestion in data["suggestions"]:
            suggestion_fields = ["title", "description", "category_name", 
                               "relevance_score", "explanation", "supporting_data"]
            for field in suggestion_fields:
                assert field in suggestion
            
            # Validate relevance score range
            assert 0.0 <= suggestion["relevance_score"] <= 1.0
            
            # Validate supporting data is a dict
            assert isinstance(suggestion["supporting_data"], dict)


class TestAchievementIntegration:
    """Integration tests combining service and endpoint functionality."""


    def test_achievement_rbac_consistency(self, test_client: TestClient, db_session):
        """Test that RBAC is consistently enforced across all achievement endpoints."""
        with patch('app.core.seed_data.SessionLocal', return_value=db_session):
            seed_database()

        schools = db_session.query(School).all()
        
        # Get students and teachers from different schools
        student_school1 = db_session.query(Student).filter(
            Student.school_id == schools[0].id
        ).first()
        teacher_school2 = db_session.query(User).filter(
            User.school_id == schools[1].id
        ).first()
        
        term = db_session.query(Term).filter(
            Term.school_id == student_school1.school_id
        ).first()

        # Login as teacher from different school
        login_response = test_client.post(
            f"{settings.API_V1_STR}/auth/login",
            json={
                "email": teacher_school2.email,
                "password": TEST_PASSWORD,
            },
        )
        assert login_response.status_code == 200

        # Should be denied access
        response = test_client.get(
            f"{settings.API_V1_STR}/achievements/suggest/{student_school1.id}/{term.id}"
        )
        assert response.status_code == 404  # Access denied manifests as not found

        # Now test with teacher from same school
        teacher_school1 = db_session.query(User).filter(
            User.school_id == schools[0].id
        ).first()

        login_response = test_client.post(
            f"{settings.API_V1_STR}/auth/login",
            json={
                "email": teacher_school1.email,
                "password": TEST_PASSWORD,
            },
        )
        assert login_response.status_code == 200

        # Should have access
        response = test_client.get(
            f"{settings.API_V1_STR}/achievements/suggest/{student_school1.id}/{term.id}"
        )
        assert response.status_code == 200