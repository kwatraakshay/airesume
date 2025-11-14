"""Database connection and session management."""
from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Create storage directory if it doesn't exist
Path(settings.STORAGE_ROOT).mkdir(parents=True, exist_ok=True)
Path(f"{settings.STORAGE_ROOT}/db").mkdir(parents=True, exist_ok=True)

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)


def init_db():
    """Initialize database tables."""
    SQLModel.metadata.create_all(engine)
    
    # Enable foreign keys and WAL mode
    with Session(engine) as session:
        from sqlalchemy import text
        session.execute(text("PRAGMA foreign_keys = ON"))
        session.execute(text("PRAGMA journal_mode = WAL"))
        session.commit()
    
    logger.info("Database initialized")


def get_session():
    """Get database session."""
    with Session(engine) as session:
        yield session

