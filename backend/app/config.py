
"""
Configuration management for environment variables and application settings
UPDATED: Added localhost:8080 to CORS origins
"""
from pydantic_settings import BaseSettings
from typing import List
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
    
    # CORS Settings - FIXED: Added both localhost and 127.0.0.1 for port 8080
    CORS_ORIGINS: List[str] = [
        "http://localhost:8080",      # ← ADDED: Your frontend URL
        "http://127.0.0.1:8080",      # ← ADDED: Alternative localhost
        "http://localhost:5173",
        "http://localhost:3000",
        "https://your-frontend-domain.com"
    ]
    
    # AI Model Settings
    MODEL_NAME: str = "t5-small"  # CPU-friendly model
    MAX_INPUT_LENGTH: int = 3000  # Characters to feed to model
    MAX_SUMMARY_LENGTH: int = 250
    MIN_SUMMARY_LENGTH: int = 80
    
    # File Upload Settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf"]
    
    # Context Prompts
    CONTEXT_PROMPTS: dict = {
        "executive": "Summarize this document with a focus on high-level insights, strategic decisions, and actionable recommendations for business leaders.",
        "student": "Summarize this document with clear explanations, learning insights, and key concepts that are easy to understand.",
        "analyst": "Summarize this document highlighting trends, data points, statistical insights, and analytical findings.",
        "general": "Summarize this document briefly and clearly, capturing the main points and essential information."
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Initialize settings
settings = Settings()