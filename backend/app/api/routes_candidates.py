"""Candidate routes."""
import json
import logging
from uuid import UUID
from typing import List
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlmodel import Session

from app.db.database import get_session
from app.db.models import CandidateStatus
from app.schemas.candidate_schema import (
    CandidateStatusResponse,
    CandidateResultResponse,
    CandidateListResponse
)
from app.services.candidate_service import candidate_service
from app.services.storage_service import storage_service
from app.core.config import settings
from app.utils.file_utils import validate_pdf_file, get_file_size
from app.workers.tasks import process_candidate_task
from pathlib import Path
import tempfile

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.post("/upload")
async def upload_resumes(
    files: List[UploadFile] = File(...),
    session: Session = Depends(get_session)
):
    """Upload one or more resume PDFs."""
    # Validate file count
    if len(files) > settings.MAX_FILES_PER_UPLOAD:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {settings.MAX_FILES_PER_UPLOAD} files allowed"
        )
    
    if len(files) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one file is required"
        )
    
    created_candidates = []
    
    for file in files:
        # Validate file extension
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File {file.filename} is not a PDF"
            )
        
        # Save to temporary location first
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            content = await file.read()
            
            # Validate file size
            if len(content) > settings.MAX_UPLOAD_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File {file.filename} exceeds maximum size"
                )
            
            tmp_file.write(content)
            tmp_path = Path(tmp_file.name)
        
        # Validate PDF
        if not validate_pdf_file(tmp_path):
            tmp_path.unlink()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File {file.filename} is not a valid PDF"
            )
        
        # Create candidate record
        candidate = candidate_service.create_candidate(
            session=session,
            original_filename=file.filename,
            resume_path=""  # Will be set after saving
        )
        
        # Save resume to storage
        resume_path = storage_service.save_resume(
            candidate_id=candidate.id,
            source_path=tmp_path,
            original_filename=file.filename
        )
        
        # Update candidate with resume path
        candidate.resume_path = str(resume_path)
        session.add(candidate)
        session.commit()
        
        # Clean up temp file
        tmp_path.unlink()
        
        # Enqueue Celery task
        try:
            process_candidate_task.delay(str(candidate.id))
            logger.info(f"Enqueued processing task for candidate {candidate.id}")
        except Exception as e:
            logger.error(f"Failed to enqueue task for candidate {candidate.id}: {e}")
            candidate_service.mark_failed(session, candidate.id, f"Failed to enqueue task: {e}")
        
        created_candidates.append({
            "id": str(candidate.id),
            "filename": file.filename,
            "status": candidate.status.value
        })
    
    return {"message": f"Uploaded {len(created_candidates)} resume(s)", "candidates": created_candidates}


@router.get("", response_model=List[CandidateListResponse])
async def list_candidates(session: Session = Depends(get_session)):
    """List all candidates."""
    candidates = candidate_service.list_candidates(session)
    return [
        CandidateListResponse(
            id=c.id,
            original_filename=c.original_filename,
            status=c.status,
            fit_score=c.fit_score,
            recommendation=c.recommendation,
            created_at=c.created_at,
            updated_at=c.updated_at
        )
        for c in candidates
    ]


@router.get("/{candidate_id}/status", response_model=CandidateStatusResponse)
async def get_candidate_status(
    candidate_id: UUID,
    session: Session = Depends(get_session)
):
    """Get candidate status."""
    candidate = candidate_service.get_candidate(session, candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    return CandidateStatusResponse(
        id=candidate.id,
        status=candidate.status,
        fit_score=candidate.fit_score,
        recommendation=candidate.recommendation
    )


@router.get("/{candidate_id}/result", response_model=CandidateResultResponse)
async def get_candidate_result(
    candidate_id: UUID,
    session: Session = Depends(get_session)
):
    """Get candidate result."""
    candidate = candidate_service.get_candidate(session, candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    # Get extraction data
    from app.db.models import Extraction
    extraction = session.get(Extraction, candidate_id)
    raw_text = extraction.raw_text if extraction else None
    structured_data = None
    if extraction and extraction.structured_json:
        try:
            structured_data = json.loads(extraction.structured_json)
        except:
            pass
    
    # Get evaluation data
    from app.db.models import Evaluation
    evaluation = session.get(Evaluation, candidate_id)
    summary_text = evaluation.summary_text if evaluation else None
    
    return CandidateResultResponse(
        id=candidate.id,
        status=candidate.status,
        fit_score=candidate.fit_score,
        recommendation=candidate.recommendation,
        summary_text=summary_text,
        raw_text=raw_text,
        structured_data=structured_data,
        created_at=candidate.created_at,
        updated_at=candidate.updated_at
    )


@router.post("/{candidate_id}/re-evaluate")
async def re_evaluate_candidate(
    candidate_id: UUID,
    session: Session = Depends(get_session)
):
    """Re-evaluate a candidate."""
    candidate = candidate_service.get_candidate(session, candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    # Reset status to PENDING
    candidate_service.update_status(session, candidate_id, CandidateStatus.PENDING)
    
    # Enqueue task
    try:
        process_candidate_task.delay(str(candidate.id))
        return {"message": "Re-evaluation started", "candidate_id": str(candidate_id)}
    except Exception as e:
        logger.error(f"Failed to enqueue re-evaluation task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start re-evaluation"
        )

