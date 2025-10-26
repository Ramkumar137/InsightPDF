"""
SQLAlchemy database models for users and summaries
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base

class User(Base):
    """User model - stores Firebase user information"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    firebase_uid = Column(String(128), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to summaries
    summaries = relationship("Summary", back_populates="user", cascade="all, delete-orphan")

class Summary(Base):
    """Summary model - stores PDF summaries with metadata"""
    __tablename__ = "summaries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # File and context information
    file_names = Column(ARRAY(String), nullable=False)  # List of uploaded PDF names
    context_type = Column(String(50), nullable=False)  # executive/student/analyst/general
    
    # Summary content (structured as JSON text)
    overview = Column(Text, nullable=False)
    key_insights = Column(Text, nullable=False)
    risks = Column(Text, nullable=True)  # Optional for some contexts
    recommendations = Column(Text, nullable=True)  # Optional for some contexts
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to user
    user = relationship("User", back_populates="summaries")
    
    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            "id": str(self.id),
            "userId": str(self.user_id),
            "fileName": self.file_names[0] if self.file_names else "Unknown",
            "fileNames": self.file_names,
            "contextType": self.context_type,
            "content": {
                "overview": self.overview,
                "keyInsights": self.key_insights,
                "risks": self.risks or "",
                "recommendations": self.recommendations or ""
            },
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat()
        }
    
    def to_history_dict(self):
        """Simplified version for history list"""
        return {
            "id": str(self.id),
            "fileName": self.file_names[0] if self.file_names else "Unknown",
            "contextType": self.context_type,
            "timestamp": self.created_at.isoformat(),
            "previewText": self.overview[:100] + "..." if len(self.overview) > 100 else self.overview
        }