from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/pdf_summarizer")

    # Firebase
    FIREBASE_CREDENTIALS_PATH: Optional[str] = os.getenv("FIREBASE_CREDENTIALS_PATH", None)
    FIREBASE_CREDENTIALS_JSON: Optional[str] = os.getenv("FIREBASE_CREDENTIALS_JSON", None)

    # CORS
    CORS_ORIGINS: list = ["http://localhost:8000", "http://localhost:5173"]

    # App Settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    MAX_FILES: int = 5
    UPLOAD_DIR: str = "uploads"

    # Model Settings
    MODEL_NAME: str = "t5-small"
    MAX_INPUT_LENGTH: int = 3000
    MAX_SUMMARY_LENGTH: int = 250
    MIN_SUMMARY_LENGTH: int = 80

    class Config:
        env_file = ".env"


settings = Settings()