"""Health check routes."""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/health", tags=["health"])


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str


@router.get("", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    from app.core.config import settings
    return HealthResponse(status="healthy", version=settings.VERSION)

