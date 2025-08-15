import time

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models import User
from app.schemas.report_schemas import ReportGenerationRequest, ReportGenerationResponse
from app.services.report_service import ReportService

router = APIRouter()


@router.post("/generate/{student_id}/{term_id}")
async def generate_student_report(
    student_id: int,
    term_id: int,
    report_data: ReportGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate PDF report for a student in a specific term.
    
    Creates a professional PDF report containing:
    - Student information and academic details
    - Grade performance with subject scores
    - Selected achievements and descriptions
    - Teacher behavioral comments
    - Professional formatting suitable for printing
    
    Access controlled by user role:
    - Form teachers: Only assigned students
    - Year heads: All students in their school  
    - Admins: All students in their school
    
    Returns PDF file as downloadable attachment with proper filename.
    """
    start_time = time.time()
    
    try:
        report_service = ReportService(db)
        
        # Generate PDF bytes
        pdf_bytes = report_service.generate_pdf_report(
            student_id, term_id, report_data, current_user
        )
        
        # Get report metadata for filename generation
        metadata = report_service.get_report_metadata(student_id, term_id, current_user)
        if not metadata:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student or term not found"
            )
            
        # Generate filename
        student_name = metadata["student_name"].replace(" ", "_")
        filename = f"{student_name}_Term_{term_id}_Report.pdf"
        
        # Return PDF as downloadable response
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(pdf_bytes)),
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (RBAC, not found, etc.)
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF generation failed: {str(e)}"
        )


@router.get("/download/{student_id}/{term_id}")
async def download_report(
    student_id: int,
    term_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Download PDF report with minimal data for quick generation.
    
    Alternative endpoint for basic report download without custom achievements
    or behavioral comments. Uses default values for quick report generation.
    
    Access controlled by user role:
    - Form teachers: Only assigned students
    - Year heads: All students in their school
    - Admins: All students in their school
    
    Returns PDF file as downloadable attachment.
    """
    # Create minimal report data for basic PDF
    basic_report_data = ReportGenerationRequest(
        selected_achievements=[],
        behavioral_comments="Generated automatically for download"
    )
    
    return await generate_student_report(
        student_id, term_id, basic_report_data, current_user, db
    )


@router.get("/metadata/{student_id}/{term_id}")
async def get_report_metadata(
    student_id: int,
    term_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get report metadata without generating the PDF.
    
    Useful for validating report data availability and preview information
    before actual PDF generation.
    
    Access controlled by user role:
    - Form teachers: Only assigned students
    - Year heads: All students in their school
    - Admins: All students in their school
    
    Returns report metadata including student info, term details, and grade count.
    """
    report_service = ReportService(db)
    metadata = report_service.get_report_metadata(student_id, term_id, current_user)
    
    if not metadata:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found or access denied"
        )
    
    return metadata