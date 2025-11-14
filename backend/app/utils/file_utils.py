"""File utility functions."""
from pathlib import Path
from typing import List
import logging

logger = logging.getLogger(__name__)


def ensure_directory(path: str) -> Path:
    """Ensure directory exists, create if not."""
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def get_candidate_directory(candidate_id: str, base_path: str) -> Path:
    """Get or create candidate-specific directory."""
    candidate_dir = Path(base_path) / candidate_id
    candidate_dir.mkdir(parents=True, exist_ok=True)
    return candidate_dir


def validate_pdf_file(file_path: Path) -> bool:
    """Validate that file is a PDF."""
    if not file_path.exists():
        return False
    if file_path.suffix.lower() != ".pdf":
        return False
    # Check magic bytes
    try:
        with open(file_path, "rb") as f:
            header = f.read(4)
            return header == b"%PDF"
    except Exception as e:
        logger.error(f"Error validating PDF: {e}")
        return False


def get_file_size(file_path: Path) -> int:
    """Get file size in bytes."""
    return file_path.stat().st_size

