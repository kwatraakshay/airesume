"""Pydantic schemas for API requests/responses."""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from app.db.models import CandidateStatus


class CandidateCreate(BaseModel):
    """Schema for creating a candidate."""
    original_filename: str
    resume_path: str


class CandidateStatusResponse(BaseModel):
    """Schema for candidate status response."""
    id: UUID
    status: CandidateStatus
    fit_score: Optional[float] = None
    recommendation: Optional[str] = None


class CandidateResultResponse(BaseModel):
    """Schema for candidate result response."""
    id: UUID
    status: CandidateStatus
    fit_score: Optional[float] = None
    recommendation: Optional[str] = None
    summary_text: Optional[str] = None
    raw_text: Optional[str] = None
    structured_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class CandidateListResponse(BaseModel):
    """Schema for candidate list response."""
    id: UUID
    original_filename: str
    status: CandidateStatus
    fit_score: Optional[float] = None
    recommendation: Optional[str] = None
    created_at: datetime
    updated_at: datetime

