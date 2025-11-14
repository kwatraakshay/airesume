"""Service for candidate management."""
import logging
from uuid import UUID
from datetime import datetime
from sqlmodel import Session, select
from typing import List, Optional

from app.db.models import Candidate, CandidateStatus, Extraction, Evaluation
from app.services.storage_service import storage_service

logger = logging.getLogger(__name__)


class CandidateService:
    """Service for candidate operations."""
    
    def create_candidate(
        self,
        session: Session,
        original_filename: str,
        resume_path: str
    ) -> Candidate:
        """Create a new candidate record."""
        candidate = Candidate(
            original_filename=original_filename,
            resume_path=str(resume_path),
            status=CandidateStatus.PENDING
        )
        session.add(candidate)
        session.commit()
        session.refresh(candidate)
        logger.info(f"Created candidate {candidate.id}")
        return candidate
    
    def get_candidate(self, session: Session, candidate_id: UUID) -> Optional[Candidate]:
        """Get candidate by ID."""
        return session.get(Candidate, candidate_id)
    
    def update_status(
        self,
        session: Session,
        candidate_id: UUID,
        status: CandidateStatus
    ) -> Candidate:
        """Update candidate status."""
        candidate = self.get_candidate(session, candidate_id)
        if not candidate:
            raise ValueError(f"Candidate {candidate_id} not found")
        
        candidate.status = status
        candidate.updated_at = datetime.utcnow()
        session.add(candidate)
        session.commit()
        session.refresh(candidate)
        return candidate
    
    def save_extraction(
        self,
        session: Session,
        candidate_id: UUID,
        raw_text: str,
        structured_json: str,
        error_log: Optional[str] = None
    ) -> Extraction:
        """Save extraction data."""
        # Check if extraction already exists
        existing = session.get(Extraction, candidate_id)
        if existing:
            existing.raw_text = raw_text
            existing.structured_json = structured_json
            existing.error_log = error_log
            extraction = existing
        else:
            extraction = Extraction(
                candidate_id=candidate_id,
                raw_text=raw_text,
                structured_json=structured_json,
                error_log=error_log
            )
            session.add(extraction)
        session.commit()
        session.refresh(extraction)
        return extraction
    
    def save_evaluation(
        self,
        session: Session,
        candidate_id: UUID,
        fit_score: float,
        recommendation: str,
        summary_text: str,
        model_used: str,
        prompt_used: Optional[str] = None
    ) -> Evaluation:
        """Save evaluation data."""
        # Check if evaluation already exists
        existing = session.get(Evaluation, candidate_id)
        if existing:
            existing.fit_score = fit_score
            existing.recommendation = recommendation
            existing.summary_text = summary_text
            existing.model_used = model_used
            existing.prompt_used = prompt_used
            evaluation = existing
        else:
            evaluation = Evaluation(
                candidate_id=candidate_id,
                fit_score=fit_score,
                recommendation=recommendation,
                summary_text=summary_text,
                model_used=model_used,
                prompt_used=prompt_used
            )
            session.add(evaluation)
        session.commit()
        session.refresh(evaluation)
        return evaluation
    
    def update_candidate_result(
        self,
        session: Session,
        candidate_id: UUID,
        fit_score: float,
        recommendation: str,
        summary_path: str
    ) -> Candidate:
        """Update candidate with final results."""
        candidate = self.get_candidate(session, candidate_id)
        if not candidate:
            raise ValueError(f"Candidate {candidate_id} not found")
        
        candidate.fit_score = fit_score
        candidate.recommendation = recommendation
        candidate.summary_path = summary_path
        candidate.status = CandidateStatus.DONE
        candidate.updated_at = datetime.utcnow()
        session.add(candidate)
        session.commit()
        session.refresh(candidate)
        return candidate
    
    def mark_failed(
        self,
        session: Session,
        candidate_id: UUID,
        error_message: str
    ) -> Candidate:
        """Mark candidate as failed and log error."""
        candidate = self.get_candidate(session, candidate_id)
        if not candidate:
            raise ValueError(f"Candidate {candidate_id} not found")
        
        # Save error log
        storage_service.save_text_file(candidate_id, "error.log", error_message)
        
        # Update extraction with error
        extraction = session.get(Extraction, candidate_id)
        if extraction:
            extraction.error_log = error_message
        else:
            extraction = Extraction(
                candidate_id=candidate_id,
                error_log=error_message
            )
        session.merge(extraction)
        
        # Update candidate status
        candidate.status = CandidateStatus.FAILED
        candidate.updated_at = datetime.utcnow()
        session.add(candidate)
        session.commit()
        session.refresh(candidate)
        return candidate
    
    def list_candidates(self, session: Session) -> List[Candidate]:
        """List all candidates."""
        statement = select(Candidate).order_by(Candidate.created_at.desc())
        return list(session.exec(statement).all())


candidate_service = CandidateService()

