"""Database models using SQLModel."""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum


class CandidateStatus(str, Enum):
    """Candidate processing status."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    DONE = "DONE"
    FAILED = "FAILED"


class Candidate(SQLModel, table=True):
    """Candidate model."""
    __tablename__ = "candidates"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    original_filename: str
    resume_path: str
    status: CandidateStatus = Field(default=CandidateStatus.PENDING)
    fit_score: Optional[float] = None
    recommendation: Optional[str] = None
    summary_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    extraction: Optional["Extraction"] = Relationship(back_populates="candidate", sa_relationship_kwargs={"uselist": False})
    evaluation: Optional["Evaluation"] = Relationship(back_populates="candidate", sa_relationship_kwargs={"uselist": False})


class Extraction(SQLModel, table=True):
    """Extraction model for raw and structured data."""
    __tablename__ = "extractions"
    
    candidate_id: UUID = Field(foreign_key="candidates.id", primary_key=True)
    raw_text: Optional[str] = None
    structured_json: Optional[str] = None  # JSON string
    error_log: Optional[str] = None
    
    # Relationship
    candidate: Optional[Candidate] = Relationship(back_populates="extraction")


class Evaluation(SQLModel, table=True):
    """Evaluation model for AI-generated results."""
    __tablename__ = "evaluations"
    
    candidate_id: UUID = Field(foreign_key="candidates.id", primary_key=True)
    fit_score: Optional[float] = None
    recommendation: Optional[str] = None
    summary_text: Optional[str] = None
    model_used: Optional[str] = None
    prompt_used: Optional[str] = None
    
    # Relationship
    candidate: Optional[Candidate] = Relationship(back_populates="evaluation")

