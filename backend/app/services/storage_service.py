"""Storage service for file operations."""
import shutil
from pathlib import Path
from typing import Optional
from uuid import UUID
import logging

from app.core.config import settings
from app.utils.file_utils import get_candidate_directory

logger = logging.getLogger(__name__)


class StorageService:
    """Service for managing file storage."""
    
    def __init__(self):
        self.storage_root = Path(settings.STORAGE_ROOT)
        self.candidates_dir = Path(settings.CANDIDATES_DIR)
        self.candidates_dir.mkdir(parents=True, exist_ok=True)
    
    def save_resume(self, candidate_id: UUID, source_path: Path, original_filename: str) -> Path:
        """Save resume file to candidate directory."""
        candidate_dir = get_candidate_directory(str(candidate_id), self.candidates_dir)
        destination = candidate_dir / "resume.pdf"
        
        shutil.copy2(source_path, destination)
        logger.info(f"Saved resume for candidate {candidate_id} to {destination}")
        return destination
    
    def get_candidate_dir(self, candidate_id: UUID) -> Path:
        """Get candidate directory path."""
        return get_candidate_directory(str(candidate_id), self.candidates_dir)
    
    def save_text_file(self, candidate_id: UUID, filename: str, content: str) -> Path:
        """Save text content to candidate directory."""
        candidate_dir = self.get_candidate_dir(candidate_id)
        file_path = candidate_dir / filename
        file_path.write_text(content, encoding="utf-8")
        logger.info(f"Saved {filename} for candidate {candidate_id}")
        return file_path
    
    def save_json_file(self, candidate_id: UUID, filename: str, data: dict) -> Path:
        """Save JSON data to candidate directory."""
        import json
        candidate_dir = self.get_candidate_dir(candidate_id)
        file_path = candidate_dir / filename
        file_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        logger.info(f"Saved {filename} for candidate {candidate_id}")
        return file_path
    
    def read_text_file(self, candidate_id: UUID, filename: str) -> Optional[str]:
        """Read text file from candidate directory."""
        candidate_dir = self.get_candidate_dir(candidate_id)
        file_path = candidate_dir / filename
        if file_path.exists():
            return file_path.read_text(encoding="utf-8")
        return None
    
    def read_json_file(self, candidate_id: UUID, filename: str) -> Optional[dict]:
        """Read JSON file from candidate directory."""
        import json
        candidate_dir = self.get_candidate_dir(candidate_id)
        file_path = candidate_dir / filename
        if file_path.exists():
            return json.loads(file_path.read_text(encoding="utf-8"))
        return None
    
    def get_resume_path(self, candidate_id: UUID) -> Path:
        """Get resume file path."""
        candidate_dir = self.get_candidate_dir(candidate_id)
        return candidate_dir / "resume.pdf"


storage_service = StorageService()

