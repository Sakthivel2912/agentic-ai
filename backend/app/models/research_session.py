"""
AI Council - Research Session Model (SQLAlchemy)
"""
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, JSON, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.sqlite import Base
from enum import Enum


class SessionStatus(str, Enum):
    """Research session status"""
    DRAFT = "draft"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ResearchCategory(str, Enum):
    """Research category enumeration"""
    GENERAL = "general"
    SOFTWARE_ARCHITECTURE = "software_architecture"
    BUSINESS_STRATEGY = "business_strategy"
    PRODUCT_RESEARCH = "product_research"
    DATA_ANALYSIS = "data_analysis"
    SECURITY = "security"
    TECHNOLOGY = "technology"
    MARKET_RESEARCH = "market_research"


class ResearchSession(Base):
    """
    Research Session Model (SQLAlchemy)
    """
    __tablename__ = "research_sessions"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    question = Column(Text, nullable=False)
    category = Column(SQLEnum(ResearchCategory), default=ResearchCategory.GENERAL)
    priority = Column(String, default="medium")
    status = Column(SQLEnum(SessionStatus), default=SessionStatus.DRAFT)
    progress = Column(Float, default=0.0)
    current_stage = Column(String, nullable=True, default="")

    # Configuration
    selected_agents = Column(JSON, default=list)
    selected_document_ids = Column(JSON, default=list)
    enable_rag = Column(Boolean, default=False)
    enable_review = Column(Boolean, default=True)
    enable_citations = Column(Boolean, default=False)

    # Results
    agent_outputs = Column(JSON, default=dict)
    reviewer_feedback = Column(JSON, default=dict, nullable=True)
    final_answer = Column(Text, nullable=True)
    sources = Column(JSON, default=list)
    session_metadata = Column(JSON, default=dict)

    # Error handling
    error_message = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    def to_dict(self):
        """Convert to dictionary"""
        updated_at = self.updated_at or self.created_at or datetime.utcnow()
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "title": self.title,
            "question": self.question,
            "category": self.category.value if self.category else None,
            "priority": self.priority,
            "status": self.status.value if self.status else None,
            "progress": self.progress,
            "current_stage": self.current_stage or "",
            "selected_agents": self.selected_agents or [],
            "selected_document_ids": self.selected_document_ids or [],
            "enable_rag": self.enable_rag,
            "enable_review": self.enable_review,
            "enable_citations": self.enable_citations,
            "agent_outputs": self.agent_outputs or {},
            "reviewer_feedback": self.reviewer_feedback or {},
            "final_answer": self.final_answer,
            "sources": self.sources or [],
            "error_message": self.error_message,
            "metadata": self.session_metadata or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": updated_at.isoformat() if hasattr(updated_at, 'isoformat') else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
