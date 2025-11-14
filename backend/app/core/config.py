"""Application configuration."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # API Settings
    API_V1_PREFIX: str = "/api"
    PROJECT_NAME: str = "Resume AI Evaluation System"
    VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = "sqlite:///./storage/db/recruitment.db"
    
    # Storage
    STORAGE_ROOT: str = "./storage"
    CANDIDATES_DIR: str = "./storage/candidates"
    LOGS_DIR: str = "./storage/logs"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Azure OpenAI
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_DEPLOYMENT_NAME: Optional[str] = None
    # Legacy OpenAI (for backward compatibility)
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    MAX_FILES_PER_UPLOAD: int = 10
    ALLOWED_EXTENSIONS: set = {".pdf"}
    
    # Job Description (can be overridden)
    JOB_DESCRIPTION: str = """
    We are looking for a talented software engineer with experience in:
    - Python, JavaScript, or similar programming languages
    - Web development frameworks
    - Database design and management
    - API development
    - Cloud technologies
    
    The ideal candidate should have strong problem-solving skills, 
    excellent communication abilities, and a passion for technology.
    """
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

