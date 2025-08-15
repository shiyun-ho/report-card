"""
Term schemas for API responses and requests

Provides Pydantic models for term data validation and serialization.
"""

from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict


class TermBase(BaseModel):
    """Base term schema with common fields."""
    name: str
    term_number: int
    academic_year: int
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class TermResponse(TermBase):
    """Term response schema for API endpoints."""
    id: int
    school_id: int
    
    model_config = ConfigDict(from_attributes=True)


class TermCreate(TermBase):
    """Schema for creating new terms."""
    school_id: int


class TermUpdate(BaseModel):
    """Schema for updating existing terms."""
    name: Optional[str] = None
    term_number: Optional[int] = None  
    academic_year: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    
    model_config = ConfigDict(from_attributes=True)