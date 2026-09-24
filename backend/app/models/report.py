"""
AI Council - Report Model (SQLAlchemy)
"""
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from app.database.sqlite import Base
from enum import Enum


class ReportStatus(str, Enum):
    """Report generation status"""
    DRAFT = "draft"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class ReportFormat(str, Enum):
    """Report format enumeration"""
    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"
    JSON = "json"


class Report(Base):
    """
    Report Model (SQLAlchemy)
    """
    __tablename__ = "reports"
    
    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("research_sessions.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    
    # Content
    content = Column(Text, nullable=True)
    html_content = Column(Text, nullable=True)
    json_content = Column(JSON, default=dict)
    
    # Metadata
    status = Column(SQLEnum(ReportStatus), default=ReportStatus.DRAFT)
    format = Column(SQLEnum(ReportFormat), default=ReportFormat.MARKDOWN)
    
    # Sections
    sections = Column(JSON, default=list)
    
    # Sources
    sources = Column(JSON, default=list)
    
    # Metrics
    word_count = Column(Integer, nullable=True)
    character_count = Column(Integer, nullable=True)
    
    # Export
    export_path = Column(String, nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "session_id": str(self.session_id),
            "user_id": str(self.user_id),
            "title": self.title,
            "content": self.content,
            "html_content": self.html_content,
            "json_content": self.json_content or {},
            "status": self.status.value if self.status else None,
            "format": self.format.value if self.format else None,
            "sections": self.sections or [],
            "sources": self.sources or [],
            "word_count": self.word_count,
            "character_count": self.character_count,
            "export_path": self.export_path,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
