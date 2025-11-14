"""Text cleaning utilities."""
import re
from typing import Dict, Any, List, Optional


def clean_text(text: str) -> str:
    """Clean extracted text."""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)]', '', text)
    return text.strip()


def extract_email(text: str) -> Optional[str]:
    """Extract email address from text."""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    matches = re.findall(email_pattern, text)
    return matches[0] if matches else None


def extract_phone(text: str) -> Optional[str]:
    """Extract phone number from text."""
    phone_patterns = [
        r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        r'\(\d{3}\)\s?\d{3}[-.]?\d{4}',
        r'\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}'
    ]
    for pattern in phone_patterns:
        matches = re.findall(pattern, text)
        if matches:
            return matches[0]
    return None


def extract_skills(text: str) -> List[str]:
    """Extract skills from text (basic keyword matching)."""
    common_skills = [
        "Python", "JavaScript", "Java", "C++", "C#", "Go", "Rust",
        "React", "Vue", "Angular", "Node.js", "Django", "Flask", "FastAPI",
        "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite",
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "CI/CD",
        "Git", "Linux", "REST API", "GraphQL", "Microservices"
    ]
    found_skills = []
    text_lower = text.lower()
    for skill in common_skills:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    return found_skills


def extract_name(text: str) -> Optional[str]:
    """Extract name from text (first few lines)."""
    lines = text.split('\n')[:5]
    for line in lines:
        line = line.strip()
        if line and len(line.split()) >= 2 and len(line.split()) <= 4:
            # Basic heuristic: name-like pattern
            if re.match(r'^[A-Z][a-z]+(\s+[A-Z][a-z]+)+$', line):
                return line
    return None


def parse_structured_data(text: str) -> Dict[str, Any]:
    """Parse structured data from resume text."""
    cleaned = clean_text(text)
    
    structured = {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "education": [],  # Would need more sophisticated parsing
        "experience": []  # Would need more sophisticated parsing
    }
    
    return structured

