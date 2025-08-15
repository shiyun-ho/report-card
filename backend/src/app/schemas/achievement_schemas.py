from typing import Dict, List

from pydantic import BaseModel, Field


class AchievementSuggestionResponse(BaseModel):
    """Individual achievement suggestion with relevance scoring."""

    title: str
    description: str
    category_name: str
    relevance_score: float = Field(
        ..., ge=0.0, le=1.0, description="Relevance score from 0.0 to 1.0"
    )
    explanation: str
    supporting_data: Dict

    class Config:
        from_attributes = True


class StudentAchievementSuggestionsResponse(BaseModel):
    """Complete achievement suggestions response for a student in a specific term."""

    student_id: int
    term_id: int
    student_name: str
    term_name: str
    suggestions: List[AchievementSuggestionResponse]
    total_suggestions: int
    average_relevance: float = Field(
        ..., ge=0.0, le=1.0, description="Average relevance score of all suggestions"
    )

    class Config:
        from_attributes = True
