from typing import List

from pydantic import BaseModel, Field


class SelectedAchievement(BaseModel):
    """Selected achievement for inclusion in report."""
    
    title: str
    description: str
    category_name: str

    class Config:
        from_attributes = True


class ReportGenerationRequest(BaseModel):
    """Request payload for PDF report generation."""
    
    selected_achievements: List[SelectedAchievement] = Field(default_factory=list)
    behavioral_comments: str = Field(..., min_length=1, max_length=500)

    class Config:
        from_attributes = True


class ReportGenerationResponse(BaseModel):
    """Response metadata for PDF report generation."""
    
    success: bool
    filename: str
    file_size: int
    generation_time_ms: int
    message: str

    class Config:
        from_attributes = True