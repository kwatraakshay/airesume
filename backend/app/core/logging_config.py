"""Logging configuration."""
import logging
import sys
from pathlib import Path
from app.core.config import settings


def setup_logging():
    """Configure application logging."""
    # Create logs directory if it doesn't exist
    Path(settings.LOGS_DIR).mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(f"{settings.LOGS_DIR}/app.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("celery").setLevel(logging.INFO)
    
    return logging.getLogger(__name__)


logger = setup_logging()

