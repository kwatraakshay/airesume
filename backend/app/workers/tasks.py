"""Celery tasks for candidate processing."""
import json
import logging
from uuid import UUID
from celery import Celery
from sqlmodel import Session

from app.core.config import settings
from app.db.database import engine
from app.db.models import CandidateStatus
from app.services.candidate_service import candidate_service
from app.services.extraction_service import extraction_service
from app.services.ai_evaluation_service import ai_evaluation_service, load_job_description
from app.services.storage_service import storage_service

logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    "resume_ai",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minutes
    task_soft_time_limit=540,  # 9 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50
)


@celery_app.task(bind=True, max_retries=3, autoretry_for=(Exception,))
def process_candidate_task(self, candidate_id: str):
    """
    Process candidate resume through full pipeline.
    
    Pipeline:
    1. Initialize and set status to PROCESSING
    2. Extract PDF text
    3. Parse structured data
    4. AI evaluation
    5. Save results to DB
    6. Update status to DONE
    """
    candidate_uuid = UUID(candidate_id)
    session = Session(engine)
    
    try:
        logger.info(f"Starting processing for candidate {candidate_id}")
        
        # Step 1: Initialize
        candidate = candidate_service.get_candidate(session, candidate_uuid)
        if not candidate:
            raise ValueError(f"Candidate {candidate_id} not found")
        
        # Ensure candidate directory exists
        storage_service.get_candidate_dir(candidate_uuid)
        
        # Update status to PROCESSING
        candidate_service.update_status(session, candidate_uuid, CandidateStatus.PROCESSING)
        logger.info(f"Set status to PROCESSING for candidate {candidate_id}")
        
        # Step 2: Extract PDF text
        try:
            raw_text, structured_data = extraction_service.extract_resume(candidate_uuid)
            logger.info(f"Extracted text for candidate {candidate_id}")
        except Exception as e:
            error_msg = f"Extraction failed: {str(e)}"
            logger.error(error_msg)
            candidate_service.mark_failed(session, candidate_uuid, error_msg)
            return {"status": "failed", "error": error_msg}
        
        # Save extraction to DB
        structured_json = json.dumps(structured_data)
        candidate_service.save_extraction(
            session=session,
            candidate_id=candidate_uuid,
            raw_text=raw_text,
            structured_json=structured_json
        )
        logger.info(f"Saved extraction data for candidate {candidate_id}")
        
        # Step 3: AI Evaluation
        try:
            # Load job description
            job_description = load_job_description()
            
            evaluation = ai_evaluation_service.evaluate_resume(
                candidate_uuid,
                raw_text,
                structured_data,
                job_description=job_description
            )
            logger.info(f"Completed AI evaluation for candidate {candidate_id}")
        except Exception as e:
            error_msg = f"AI evaluation failed: {str(e)}"
            logger.error(error_msg)
            candidate_service.mark_failed(session, candidate_uuid, error_msg)
            return {"status": "failed", "error": error_msg}
        
        # Step 4: Save evaluation to DB
        # Determine which model was used
        if settings.AZURE_OPENAI_DEPLOYMENT_NAME:
            model_used = settings.AZURE_OPENAI_DEPLOYMENT_NAME
        else:
            model_used = settings.OPENAI_MODEL
        
        candidate_service.save_evaluation(
            session=session,
            candidate_id=candidate_uuid,
            fit_score=float(evaluation["fit_score"]),
            recommendation=evaluation["recommendation"],
            summary_text=evaluation["summary_text"],
            model_used=model_used
        )
        logger.info(f"Saved evaluation data for candidate {candidate_id}")
        
        # Step 5: Update candidate with final results
        summary_path = str(storage_service.get_candidate_dir(candidate_uuid) / "summary.txt")
        candidate_service.update_candidate_result(
            session=session,
            candidate_id=candidate_uuid,
            fit_score=float(evaluation["fit_score"]),
            recommendation=evaluation["recommendation"],
            summary_path=summary_path
        )
        logger.info(f"Completed processing for candidate {candidate_id}")
        
        return {
            "status": "success",
            "candidate_id": candidate_id,
            "fit_score": evaluation["fit_score"],
            "recommendation": evaluation["recommendation"]
        }
        
    except Exception as e:
        error_msg = f"Processing failed: {str(e)}"
        logger.error(f"Error processing candidate {candidate_id}: {e}", exc_info=True)
        try:
            candidate_service.mark_failed(session, candidate_uuid, error_msg)
        except:
            pass
        raise  # Re-raise for Celery retry
    
    finally:
        session.close()

