"""Service for extracting and parsing resume data."""
import json
import logging
from pathlib import Path
from uuid import UUID

from app.services.storage_service import storage_service
from app.utils.pdf_utils import extract_pdf_text
from app.utils.text_cleaner import parse_structured_data

logger = logging.getLogger(__name__)


class ExtractionService:
    """Service for resume extraction."""
    
    def extract_resume(self, candidate_id: UUID) -> tuple[str, dict]:
        """
        Extract text and structured data from resume.
        Returns: (raw_text, structured_data)
        """
        logger.info(f"Extracting resume for candidate {candidate_id}")
        
        # Get resume path
        resume_path = storage_service.get_resume_path(candidate_id)
        
        if not resume_path.exists():
            raise FileNotFoundError(f"Resume not found: {resume_path}")
        
        # Extract text
        raw_text = extract_pdf_text(resume_path)
        
        # Save extracted text
        storage_service.save_text_file(candidate_id, "extracted_text.txt", raw_text)
        
        # Parse structured data
        structured_data = parse_structured_data(raw_text)
        
        # Save structured JSON
        storage_service.save_json_file(candidate_id, "structured.json", structured_data)
        
        logger.info(f"Successfully extracted resume for candidate {candidate_id}")
        return raw_text, structured_data


extraction_service = ExtractionService()

