from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models import User
from app.schemas.achievement_schemas import StudentAchievementSuggestionsResponse
from app.services.achievement_service import AchievementService

router = APIRouter()


@router.get("/suggest/{student_id}/{term_id}", response_model=StudentAchievementSuggestionsResponse)
async def suggest_achievements(
    student_id: int,
    term_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get achievement suggestions for a student in a specific term.

    Returns suggested achievements from shared database based on grade patterns
    with relevance indicators and supporting data.

    Access controlled by user role:
    - Form teachers: Only assigned students
    - Year heads: All students in their school
    - Admins: All students in their school

    Suggestions based on:
    - Subject-specific improvements (≥20% significant, 10-19% steady progress)
    - Excellence achievements (≥90 scores)
    - Overall academic improvement (≥15% across subjects)
    - Consistent high performance (≥85 average)
    """
    achievement_service = AchievementService(db)
    suggestions = achievement_service.get_achievement_suggestions(student_id, term_id, current_user)

    if not suggestions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found or insufficient data for suggestions",
        )

    return StudentAchievementSuggestionsResponse(**suggestions)
