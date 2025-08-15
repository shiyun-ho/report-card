"""Tests for PDF report generation functionality."""
from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException

from app.core.seed_data import seed_database
from app.models import School, Student, Term, User, UserRole
from app.schemas.report_schemas import ReportGenerationRequest
from app.services.report_service import ReportService


class TestReportService:
    """Test cases for ReportService class."""

    def test_report_service_initialization(self, db_session):
        """Test ReportService can be initialized properly."""
        service = ReportService(db_session)
        assert service.db == db_session
        assert service.student_service is not None
        assert service.grade_service is not None
        assert service.achievement_service is not None
        assert service.template_env is not None

    def test_can_generate_report_form_teacher_authorized(self, db_session):
        """Test form teacher can generate reports for assigned students."""
        with patch('app.core.seed_data.SessionLocal', return_value=db_session):
            seed_database()

        service = ReportService(db_session)

        # Get first student and their form teacher from same school
        student = db_session.query(Student).first()
        form_teacher = db_session.query(User).filter(
            User.role == UserRole.FORM_TEACHER,
            User.school_id == student.school_id
        ).first()

        assert service.can_generate_report(form_teacher, student.id)

    def test_can_generate_report_cross_school_denied(self, db_session):
        """Test teacher cannot generate reports for students from different school."""
        with patch('app.core.seed_data.SessionLocal', return_value=db_session):
            seed_database()

        service = ReportService(db_session)

        # Get student from one school and teacher from another
        schools = db_session.query(School).all()
        assert len(schools) >= 2, "Need at least 2 schools for this test"

        student_school1 = db_session.query(Student).filter(
            Student.school_id == schools[0].id
        ).first()
        teacher_school2 = db_session.query(User).filter(
            User.school_id == schools[1].id
        ).first()

        assert not service.can_generate_report(teacher_school2, student_school1.id)

    def test_can_generate_report_year_head_access(self, db_session):
        """Test year head can generate reports for all students in their school."""
        with patch('app.core.seed_data.SessionLocal', return_value=db_session):
            seed_database()

        service = ReportService(db_session)

        # Get any student and a year head from same school
        student = db_session.query(Student).first()
        year_head = db_session.query(User).filter(
            User.role == UserRole.YEAR_HEAD,
            User.school_id == student.school_id
        ).first()

        assert service.can_generate_report(year_head, student.id)

    @patch('app.services.report_service.HTML')
    def test_generate_pdf_returns_valid_bytes(self, mock_html, db_session):
        """Test PDF generation returns valid bytes with mocked WeasyPrint."""
        with patch('app.core.seed_data.SessionLocal', return_value=db_session):
            seed_database()

        # Mock PDF generation to return bytes
        mock_pdf = Mock()
        mock_pdf.write_pdf.return_value = b'mock_pdf_content'
        mock_html.return_value = mock_pdf

        service = ReportService(db_session)

        # Get student, teacher, and term
        student = db_session.query(Student).first()
        teacher = db_session.query(User).filter(
            User.school_id == student.school_id
        ).first()
        term = db_session.query(Term).filter(
            Term.school_id == student.school_id
        ).first()

        # Create minimal report data
        report_data = ReportGenerationRequest(
            selected_achievements=[],
            behavioral_comments="Test behavioral comments for PDF generation"
        )

        result = service.generate_pdf_report(student.id, term.id, report_data, teacher)

        assert isinstance(result, bytes)
        assert len(result) > 0
        assert result == b'mock_pdf_content'

        # Verify HTML was called for PDF generation
        mock_html.assert_called_once()
        mock_pdf.write_pdf.assert_called_once()

    @patch('app.services.report_service.HTML')
    def test_generate_pdf_access_denied_403(self, mock_html, db_session):
        """Test PDF generation raises 403 when user has no access to student."""
        with patch('app.core.seed_data.SessionLocal', return_value=db_session):
            seed_database()

        service = ReportService(db_session)

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

        report_data = ReportGenerationRequest(
            selected_achievements=[],
            behavioral_comments="Test comments"
        )

        with pytest.raises(HTTPException) as exc_info:
            service.generate_pdf_report(student_school1.id, term.id, report_data, teacher_school2)

        assert exc_info.value.status_code == 403
        assert "access denied" in exc_info.value.detail.lower()

        # Verify HTML was not called since access was denied
        mock_html.assert_not_called()

    @patch('app.services.report_service.HTML')
    def test_generate_pdf_student_not_found_404(self, mock_html, db_session):
        """Test PDF generation raises 403 when student doesn't exist (RBAC first)."""
        with patch('app.core.seed_data.SessionLocal', return_value=db_session):
            seed_database()

        service = ReportService(db_session)
        teacher = db_session.query(User).first()
        term = db_session.query(Term).filter(
            Term.school_id == teacher.school_id
        ).first()

        report_data = ReportGenerationRequest(
            selected_achievements=[],
            behavioral_comments="Test comments"
        )

        with pytest.raises(HTTPException) as exc_info:
            service.generate_pdf_report(99999, term.id, report_data, teacher)

        # RBAC check fails first for non-existent student, returns 403
        assert exc_info.value.status_code == 403
        assert "access denied" in exc_info.value.detail.lower()

        # Verify HTML was not called since access was denied
        mock_html.assert_not_called()

    @patch('app.services.report_service.HTML')
    def test_generate_pdf_term_not_found_404(self, mock_html, db_session):
        """Test PDF generation raises 500 when term doesn't exist (wrapped 404)."""
        with patch('app.core.seed_data.SessionLocal', return_value=db_session):
            seed_database()

        service = ReportService(db_session)
        student = db_session.query(Student).first()
        teacher = db_session.query(User).filter(
            User.school_id == student.school_id
        ).first()

        report_data = ReportGenerationRequest(
            selected_achievements=[],
            behavioral_comments="Test comments"
        )

        with pytest.raises(HTTPException) as exc_info:
            service.generate_pdf_report(student.id, 99999, report_data, teacher)

        # Service wraps 404 in 500 due to try-catch in generate_pdf_report
        assert exc_info.value.status_code == 500
        assert "pdf generation failed" in exc_info.value.detail.lower()
        assert "term not found" in exc_info.value.detail.lower()

        # Verify HTML was not called since term was not found
        mock_html.assert_not_called()

    def test_get_report_metadata_success(self, db_session):
        """Test successful report metadata retrieval."""
        with patch('app.core.seed_data.SessionLocal', return_value=db_session):
            seed_database()

        service = ReportService(db_session)

        # Get student, teacher, and term
        student = db_session.query(Student).first()
        teacher = db_session.query(User).filter(
            User.school_id == student.school_id
        ).first()
        term = db_session.query(Term).filter(
            Term.school_id == student.school_id
        ).first()

        metadata = service.get_report_metadata(student.id, term.id, teacher)

        assert metadata is not None
        assert isinstance(metadata, dict)

        # Verify required metadata fields
        assert "student_name" in metadata
        assert "student_id" in metadata
        assert "class_name" in metadata
        assert "term_name" in metadata
        assert "term_number" in metadata
        assert "academic_year" in metadata
        assert "total_subjects" in metadata
        assert "has_grades" in metadata

        # Verify metadata values
        assert metadata["student_name"] == student.full_name
        assert metadata["student_id"] == student.student_id
        assert metadata["term_name"] == term.name
        assert metadata["term_number"] == term.term_number
        assert metadata["academic_year"] == term.academic_year

    def test_get_report_metadata_no_access_returns_none(self, db_session):
        """Test report metadata returns None when user has no access."""
        with patch('app.core.seed_data.SessionLocal', return_value=db_session):
            seed_database()

        service = ReportService(db_session)

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

        metadata = service.get_report_metadata(student_school1.id, term.id, teacher_school2)

        assert metadata is None

    @patch('app.services.report_service.HTML')
    def test_compile_report_data_structure(self, mock_html, db_session):
        """Test report data compilation returns proper structure."""
        with patch('app.core.seed_data.SessionLocal', return_value=db_session):
            seed_database()

        # Mock PDF generation to avoid actual generation
        mock_pdf = Mock()
        mock_pdf.write_pdf.return_value = b'mock_pdf_content'
        mock_html.return_value = mock_pdf

        service = ReportService(db_session)

        # Get student, teacher, and term
        student = db_session.query(Student).first()
        teacher = db_session.query(User).filter(
            User.school_id == student.school_id
        ).first()
        term = db_session.query(Term).filter(
            Term.school_id == student.school_id
        ).first()

        # Create report data with achievements
        from app.schemas.report_schemas import SelectedAchievement
        report_data = ReportGenerationRequest(
            selected_achievements=[
                SelectedAchievement(
                    title="Test Achievement",
                    description="Test achievement description",
                    category_name="Test Category"
                )
            ],
            behavioral_comments="Test behavioral comments for data structure validation"
        )

        # Access the private method for testing data compilation
        template_data = service._compile_report_data(student.id, term.id, report_data, teacher)

        assert isinstance(template_data, dict)

        # Verify main data structure
        assert "student" in template_data
        assert "term" in template_data
        assert "grades" in template_data
        assert "average_score" in template_data
        assert "performance_band" in template_data
        assert "selected_achievements" in template_data
        assert "behavioral_comments" in template_data
        assert "teacher_name" in template_data
        assert "generation_date" in template_data
        assert "school_name" in template_data

        # Verify student data structure
        student_data = template_data["student"]
        assert "full_name" in student_data
        assert "student_id" in student_data
        assert "class_name" in student_data

        # Verify term data structure
        term_data = template_data["term"]
        assert "name" in term_data
        assert "term_number" in term_data
        assert "academic_year" in term_data

        # Verify achievements were included
        achievements = template_data["selected_achievements"]
        assert len(achievements) == 1
        assert achievements[0]["title"] == "Test Achievement"
        assert achievements[0]["description"] == "Test achievement description"
        assert achievements[0]["category_name"] == "Test Category"

        # Verify behavioral comments
        assert template_data["behavioral_comments"] == report_data.behavioral_comments
        assert template_data["teacher_name"] == teacher.full_name


class TestReportServiceEdgeCases:
    """Test edge cases and error conditions for ReportService."""

    def test_invalid_student_id_edge_case(self, db_session):
        """Test handling of various invalid student ID formats."""
        service = ReportService(db_session)
        teacher = User(
            id=1, school_id=1, email="test@test.com",
            full_name="Test Teacher", role=UserRole.FORM_TEACHER
        )

        # Test with negative ID
        assert not service.can_generate_report(teacher, -1)

        # Test with zero ID
        assert not service.can_generate_report(teacher, 0)

    def test_invalid_term_id_edge_case(self, db_session):
        """Test report metadata with invalid term ID."""
        with patch('app.core.seed_data.SessionLocal', return_value=db_session):
            seed_database()

        service = ReportService(db_session)
        student = db_session.query(Student).first()
        teacher = db_session.query(User).filter(
            User.school_id == student.school_id
        ).first()

        # Test with invalid term ID
        metadata = service.get_report_metadata(student.id, 99999, teacher)
        assert metadata is None

    @patch('app.services.report_service.HTML')
    def test_weasyprint_exception_handling(self, mock_html, db_session):
        """Test handling of WeasyPrint exceptions during PDF generation."""
        with patch('app.core.seed_data.SessionLocal', return_value=db_session):
            seed_database()

        # Mock HTML to raise an exception
        mock_html.side_effect = Exception("WeasyPrint error")

        service = ReportService(db_session)
        student = db_session.query(Student).first()
        teacher = db_session.query(User).filter(
            User.school_id == student.school_id
        ).first()
        term = db_session.query(Term).filter(
            Term.school_id == student.school_id
        ).first()

        report_data = ReportGenerationRequest(
            selected_achievements=[],
            behavioral_comments="Test comments"
        )

        with pytest.raises(HTTPException) as exc_info:
            service.generate_pdf_report(student.id, term.id, report_data, teacher)

        assert exc_info.value.status_code == 500
        assert "pdf generation failed" in exc_info.value.detail.lower()
