import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import HTTPException
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session
from weasyprint import HTML

from app.models.student import Student
from app.models.term import Term
from app.models.user import User
from app.schemas.report_schemas import ReportGenerationRequest
from app.services.achievement_service import AchievementService
from app.services.grade_service import GradeService
from app.services.student_service import StudentService


class ReportService:
    """
    Service for generating PDF reports with role-based access control.
    
    Implements RBAC enforcement:
    - Form teachers: Can generate reports for assigned students only
    - Year heads: Can generate reports for all students in their school
    - Admins: Can generate reports for all students in their school
    
    Uses existing service layer for data compilation and WeasyPrint
    for professional PDF generation from HTML templates.
    """

    def __init__(self, db: Session):
        self.db = db
        self.student_service = StudentService(db)
        self.grade_service = GradeService(db)
        self.achievement_service = AchievementService(db)
        
        # Initialize Jinja2 template environment
        self.template_env = Environment(
            loader=FileSystemLoader("/app/templates"),
            autoescape=True
        )

    def can_generate_report(self, user: User, student_id: int) -> bool:
        """
        Check if user can generate reports for specific student.
        
        Args:
            user: Current authenticated user
            student_id: ID of the student
            
        Returns:
            True if user can generate reports for the student, False otherwise
        """
        # Leverage existing RBAC logic from student service
        return self.student_service.can_access_student(student_id, user)

    def generate_pdf_report(
        self,
        student_id: int,
        term_id: int,
        report_data: ReportGenerationRequest,
        current_user: User,
    ) -> bytes:
        """
        Generate PDF report with RBAC enforcement.
        
        Args:
            student_id: ID of the student
            term_id: ID of the term
            report_data: Report content from request
            current_user: Current authenticated user
            
        Returns:
            PDF file content as bytes
            
        Raises:
            HTTPException: If access denied or data invalid
        """
        start_time = time.time()
        
        # RBAC: Verify access to student
        if not self.can_generate_report(current_user, student_id):
            raise HTTPException(
                status_code=403, 
                detail="Access denied: Cannot generate report for this student"
            )
            
        try:
            # Compile all report data
            template_data = self._compile_report_data(
                student_id, term_id, report_data, current_user
            )
            
            # Render HTML template
            template = self.template_env.get_template("report_card.html")
            html_content = template.render(**template_data)
            
            # Generate PDF using WeasyPrint
            pdf_bytes = HTML(string=html_content).write_pdf()
            
            generation_time = int((time.time() - start_time) * 1000)
            
            return pdf_bytes
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"PDF generation failed: {str(e)}"
            )

    def _compile_report_data(
        self,
        student_id: int,
        term_id: int,
        report_data: ReportGenerationRequest,
        current_user: User,
    ) -> Dict[str, Any]:
        """
        Compile all data needed for report template.
        
        Args:
            student_id: ID of the student
            term_id: ID of the term
            report_data: Report content from request
            current_user: Current authenticated user
            
        Returns:
            Dictionary containing all template variables
            
        Raises:
            HTTPException: If student or term not found
        """
        # Get student details with RBAC enforcement
        student = self.student_service.get_student_by_id(student_id, current_user)
        if not student:
            raise HTTPException(
                status_code=404,
                detail="Student not found or access denied"
            )
            
        # Get term details with school isolation
        term = self._get_term_by_id(term_id, current_user)
        if not term:
            raise HTTPException(
                status_code=404,
                detail="Term not found or access denied"
            )
            
        # Get grades with RBAC enforcement
        grades = self.grade_service.get_student_grades(student_id, term_id, current_user)
        
        # Calculate performance metrics
        if grades:
            total_score = sum(float(grade.score) for grade in grades)
            average_score = total_score / len(grades)
            performance_band = self.grade_service.calculate_performance_band(average_score)
        else:
            average_score = 0.0
            performance_band = "No Data"
            
        # Prepare grades data for template
        grades_data = []
        for grade in grades:
            grades_data.append({
                "subject_name": grade.subject.name,
                "score": float(grade.score),
                "subject_id": grade.subject_id,
            })
        
        return {
            "student": {
                "full_name": student.full_name,
                "student_id": student.student_id,
                "class_name": student.class_obj.name if student.class_obj else "N/A",
            },
            "term": {
                "name": term.name,
                "term_number": term.term_number,
                "academic_year": term.academic_year,
            },
            "grades": grades_data,
            "average_score": round(average_score, 1),
            "performance_band": performance_band,
            "selected_achievements": [
                {
                    "title": achievement.title,
                    "description": achievement.description,
                    "category_name": achievement.category_name,
                }
                for achievement in report_data.selected_achievements
            ],
            "behavioral_comments": report_data.behavioral_comments,
            "teacher_name": current_user.full_name,
            "generation_date": datetime.now().strftime("%B %d, %Y"),
            "school_name": student.school.name if hasattr(student, "school") else "School Name",
        }

    def _get_term_by_id(self, term_id: int, current_user: User) -> Optional[Term]:
        """
        Get term by ID with school isolation.
        
        Args:
            term_id: ID of the term
            current_user: Current authenticated user
            
        Returns:
            Term object if found and accessible, None otherwise
        """
        term = (
            self.db.query(Term)
            .filter(
                Term.id == term_id,
                Term.school_id == current_user.school_id
            )
            .first()
        )
        return term

    def get_report_metadata(
        self, student_id: int, term_id: int, current_user: User
    ) -> Optional[Dict[str, Any]]:
        """
        Get metadata for report generation without generating the actual PDF.
        
        Args:
            student_id: ID of the student
            term_id: ID of the term
            current_user: Current authenticated user
            
        Returns:
            Dictionary with report metadata or None if access denied
        """
        # Verify access
        if not self.can_generate_report(current_user, student_id):
            return None
            
        student = self.student_service.get_student_by_id(student_id, current_user)
        term = self._get_term_by_id(term_id, current_user)
        
        if not student or not term:
            return None
            
        # Get grade count for metadata
        grades = self.grade_service.get_student_grades(student_id, term_id, current_user)
        
        return {
            "student_name": student.full_name,
            "student_id": student.student_id,
            "class_name": student.class_obj.name if student.class_obj else "N/A",
            "term_name": term.name,
            "term_number": term.term_number,
            "academic_year": term.academic_year,
            "total_subjects": len(grades),
            "has_grades": len(grades) > 0,
        }