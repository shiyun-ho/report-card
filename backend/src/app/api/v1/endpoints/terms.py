"""
Terms endpoints for Report Card Assistant API

Provides endpoints for managing academic terms with RBAC integration.
Teachers can only access terms from their assigned schools.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.term import Term
from app.models.user import User
from app.schemas.term_schemas import TermResponse


router = APIRouter()


@router.get("/", response_model=List[TermResponse])
async def get_terms(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all terms for the current user's school.
    
    RBAC: Users can only see terms from their assigned school.
    
    Returns:
        List[TermResponse]: All terms for the user's school
    """
    try:
        # Get terms for current user's school only (RBAC enforcement)
        terms = (
            db.query(Term)
            .filter(Term.school_id == current_user.school_id)
            .order_by(Term.academic_year.desc(), Term.term_number.asc())
            .all()
        )
        
        return terms
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve terms: {str(e)}"
        )


@router.get("/{term_id}", response_model=TermResponse) 
async def get_term_by_id(
    term_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific term by ID.
    
    RBAC: Users can only access terms from their assigned school.
    
    Args:
        term_id: ID of the term to retrieve
        
    Returns:
        TermResponse: The requested term
        
    Raises:
        HTTPException: 404 if term not found or access denied
    """
    try:
        # Get term with RBAC enforcement
        term = (
            db.query(Term)
            .filter(
                Term.id == term_id,
                Term.school_id == current_user.school_id
            )
            .first()
        )
        
        if not term:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Term {term_id} not found or access denied"
            )
            
        return term
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve term: {str(e)}"
        )