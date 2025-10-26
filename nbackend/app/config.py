"""
Configuration management
FIXED: Added SUPABASE_JWT_SECRET field
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/pdf_summarizer"
    )
    
    # Firebase Authentication
    FIREBASE_CREDENTIALS_PATH: str = os.getenv(
        "FIREBASE_CREDENTIALS_PATH",
        "firebase-credentials.json"
    )
    
    # Supabase JWT Secret - NEW (Optional)
    SUPABASE_JWT_SECRET: Optional[str] = None
    
    # Gemini API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # CORS Settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:5173",
        "http://localhost:3000",
        "https://your-project.web.app",
        "https://your-project.firebaseapp.com",
    ]
    
    # File Upload Settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf"]
    
    # Gemini Settings
    MAX_TEXT_LENGTH: int = 50000  # Characters to send to Gemini
    
    # Context Prompts - ENHANCED
    CONTEXT_PROMPTS: dict = {
        "executive": """You are summarizing for C-level executives. Focus on:
- High-level strategic insights and business impact
- Key decisions and recommendations
- Financial implications and ROI
- Risk assessment and mitigation strategies
- Actionable next steps for leadership""",
        
        "student": """You are summarizing for students. Focus on:
- Clear explanations of key concepts
- Learning objectives and takeaways
- Important definitions and terminology
- Examples and practical applications
- Study tips and important points to remember""",
        
        "analyst": """You are summarizing for data analysts. Focus on:
- Statistical findings and data trends
- Methodology and approach
- Key metrics and quantitative insights
- Patterns, correlations, and anomalies
- Data-driven recommendations""",
        
        "general": """Provide a clear, comprehensive summary that:
- Captures the main points and key information
- Is easy to understand for a general audience
- Highlights important facts and conclusions
- Maintains objectivity and clarity"""
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        # FIXED: Allow extra fields from .env
        extra = "ignore"

settings = Settings()