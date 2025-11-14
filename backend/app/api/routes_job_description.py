"""Job description routes."""
from fastapi import APIRouter
from app.services.ai_evaluation_service import load_job_description

router = APIRouter(prefix="/job-description", tags=["job-description"])


@router.get("")
def get_job_description():
    """Get the current job description."""
    return {"job_description": load_job_description()}

