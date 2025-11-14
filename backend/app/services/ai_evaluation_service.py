"""Service for AI-powered resume evaluation."""
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from uuid import UUID

from app.core.config import settings
from app.services.storage_service import storage_service

logger = logging.getLogger(__name__)


def load_job_description() -> str:
    """Load job description from file."""
    # Get the path relative to the backend directory
    backend_dir = Path(__file__).parent.parent
    path = backend_dir / "data" / "job_description.txt"
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.warning(f"Job description file not found at {path}, using default from settings")
        return settings.JOB_DESCRIPTION


class AIEvaluationService:
    """Service for AI evaluation of resumes."""
    
    def __init__(self):
        # Azure OpenAI configuration (preferred)
        self.azure_endpoint = settings.AZURE_OPENAI_ENDPOINT
        self.azure_api_key = settings.AZURE_OPENAI_API_KEY
        self.azure_deployment_name = settings.AZURE_OPENAI_DEPLOYMENT_NAME
        
        # Legacy OpenAI configuration (fallback)
        self.openai_api_key = settings.OPENAI_API_KEY
        self.openai_model = settings.OPENAI_MODEL
        
        # Determine which service to use
        self.use_azure = bool(self.azure_endpoint and self.azure_api_key and self.azure_deployment_name)
        
        if not self.use_azure and not self.openai_api_key:
            logger.warning("Neither Azure OpenAI nor OpenAI API key is set")
        
        self.job_description = settings.JOB_DESCRIPTION
    
    def _call_openai(self, prompt: str, max_retries: int = 2) -> Dict[str, Any]:
        """Call Azure OpenAI or OpenAI API with retry logic."""
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("OpenAI library not installed")
        
        # Initialize client based on configuration
        if self.use_azure:
            # Use Azure OpenAI
            if not self.azure_endpoint or not self.azure_api_key or not self.azure_deployment_name:
                raise ValueError("Azure OpenAI configuration incomplete. Need endpoint, API key, and deployment name.")
            
            client = OpenAI(
                base_url=self.azure_endpoint,
                api_key=self.azure_api_key
            )
            model_name = self.azure_deployment_name
            logger.info("Using Azure OpenAI")
        else:
            # Use standard OpenAI
            if not self.openai_api_key:
                raise ValueError("OpenAI API key not configured")
            
            client = OpenAI(api_key=self.openai_api_key)
            model_name = self.openai_model
            logger.info("Using standard OpenAI")
        
        try:
            # Test client initialization
            pass
        except TypeError as e:
            logger.error(f"Client initialization error: {e}")
            raise ValueError(f"Failed to initialize AI client: {e}")
        
        for attempt in range(max_retries + 1):
            try:
                # Build request parameters
                request_params = {
                    "model": model_name,
                    "messages": [
                        {"role": "system", "content": "You are an expert resume evaluator. Always return valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    "response_format": {"type": "json_object"}
                }
                
                # Azure OpenAI o4-mini only supports default temperature (1), so don't set it
                # Standard OpenAI can use custom temperature
                if not self.use_azure:
                    request_params["temperature"] = 0.7
                
                response = client.chat.completions.create(**request_params)
                
                content = response.choices[0].message.content
                result = json.loads(content)
                
                # Validate required fields
                required_fields = ["fit_score", "recommendation", "strengths", "weaknesses", "summary_text"]
                for field in required_fields:
                    if field not in result:
                        raise ValueError(f"Missing required field: {field}")
                
                # Validate fit_score
                fit_score = result.get("fit_score")
                if not isinstance(fit_score, (int, float)) or not (1 <= fit_score <= 10):
                    raise ValueError(f"Invalid fit_score: {fit_score}")
                
                # Validate recommendation
                recommendation = result.get("recommendation")
                if recommendation not in ["Interview", "Decline"]:
                    raise ValueError(f"Invalid recommendation: {recommendation}")
                
                return result
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error (attempt {attempt + 1}): {e}")
                if attempt == max_retries:
                    raise
            except Exception as e:
                error_str = str(e)
                logger.error(f"OpenAI API error (attempt {attempt + 1}): {e}")
                
                # Check for quota/billing errors
                if "429" in error_str or "quota" in error_str.lower() or "insufficient_quota" in error_str.lower():
                    service_name = "Azure OpenAI" if self.use_azure else "OpenAI"
                    raise ValueError(
                        f"{service_name} API quota exceeded. Please check your account billing and quota limits."
                    )
                
                if attempt == max_retries:
                    raise
        
        service_name = "Azure OpenAI" if self.use_azure else "OpenAI"
        raise Exception(f"Failed to get valid response from {service_name} after retries")
    
    def evaluate_resume(self, candidate_id: UUID, raw_text: str, structured_data: Dict[str, Any], job_description: Optional[str] = None) -> Dict[str, Any]:
        """
        Evaluate resume using AI.
        Returns evaluation dict with fit_score, recommendation, strengths, weaknesses, summary_text
        """
        logger.info(f"Evaluating resume for candidate {candidate_id}")
        
        # Use provided job description or fall back to default
        jd = job_description if job_description else self.job_description
        
        # Build prompt
        prompt = f"""
Evaluate this resume against the following job description:

JOB DESCRIPTION:
{jd}

RESUME TEXT:
{raw_text[:4000]}

STRUCTURED DATA:
{json.dumps(structured_data, indent=2)}

Please provide a comprehensive evaluation in JSON format with the following structure:
{{
    "fit_score": <number between 1-10>,
    "recommendation": "Interview" or "Decline",
    "strengths": ["strength1", "strength2", ...],
    "weaknesses": ["weakness1", "weakness2", ...],
    "summary_text": "<2-page detailed narrative summary of the candidate's qualifications, experience, and fit for the role>"
}}

The summary_text should be approximately 2 pages (1000-1500 words) and provide a comprehensive analysis.
"""
        
        try:
            evaluation = self._call_openai(prompt)
            
            # Save evaluation JSON
            storage_service.save_json_file(candidate_id, "evaluation.json", evaluation)
            
            # Save summary text separately
            summary_text = evaluation.get("summary_text", "")
            storage_service.save_text_file(candidate_id, "summary.txt", summary_text)
            
            logger.info(f"Successfully evaluated resume for candidate {candidate_id}")
            return evaluation
            
        except Exception as e:
            logger.error(f"AI evaluation failed for candidate {candidate_id}: {e}")
            raise


ai_evaluation_service = AIEvaluationService()

