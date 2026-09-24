"""
AI Council - Evaluation Model (SQLAlchemy)
"""
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from app.database.sqlite import Base
from enum import Enum


class EvaluationStatus(str, Enum):
    """Evaluation status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Evaluation(Base):
    """
    Evaluation Model (SQLAlchemy)
    """
    __tablename__ = "evaluations"
    
    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("research_sessions.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Status
    status = Column(SQLEnum(EvaluationStatus), default=EvaluationStatus.PENDING)
    
    # Quality Metrics
    overall_score = Column(Float, nullable=True)
    relevance_score = Column(Float, nullable=True)
    completeness_score = Column(Float, nullable=True)
    accuracy_score = Column(Float, nullable=True)
    clarity_score = Column(Float, nullable=True)
    
    # Agent Performance
    agent_scores = Column(JSON, default=dict)
    
    # Feedback
    user_feedback = Column(Text, nullable=True)
    reviewer_comments = Column(Text, nullable=True)
    
    # Metrics
    agent_count = Column(Integer, nullable=True)
    total_duration = Column(Float, nullable=True)
    token_usage = Column(Integer, nullable=True)
    cost_estimate = Column(Float, nullable=True)
    
    # Comparison
    comparison_with_previous = Column(JSON, default=dict)
    
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
            "status": self.status.value if self.status else None,
            "overall_score": self.overall_score,
            "relevance_score": self.relevance_score,
            "completeness_score": self.completeness_score,
            "accuracy_score": self.accuracy_score,
            "clarity_score": self.clarity_score,
            "agent_scores": self.agent_scores or {},
            "user_feedback": self.user_feedback,
            "reviewer_comments": self.reviewer_comments,
            "agent_count": self.agent_count,
            "total_duration": self.total_duration,
            "token_usage": self.token_usage,
            "cost_estimate": self.cost_estimate,
            "comparison_with_previous": self.comparison_with_previous or {},
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
