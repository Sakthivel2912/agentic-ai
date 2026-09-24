"""
AI Council - Agent Execution Model (SQLAlchemy)
"""
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from app.database.sqlite import Base
from enum import Enum


class AgentStatus(str, Enum):
    """Agent execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentType(str, Enum):
    """Agent type enumeration"""
    RESEARCH = "research"
    TECHNICAL = "technical"
    COST = "cost"
    DATA = "data"
    PRODUCT = "product"
    SECURITY = "security"
    REVIEWER = "reviewer"
    SYNTHESIZER = "synthesizer"


class AgentExecution(Base):
    """
    Agent Execution Model (SQLAlchemy)
    """
    __tablename__ = "agent_executions"
    
    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("research_sessions.id"), nullable=False, index=True)
    agent_id = Column(String, nullable=False, index=True)
    agent_name = Column(String, nullable=False)
    agent_type = Column(SQLEnum(AgentType), nullable=False)
    status = Column(SQLEnum(AgentStatus), default=AgentStatus.PENDING)
    
    # Timing
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Float, nullable=True)
    
    # Input/Output
    input_data = Column(JSON, default=dict)
    raw_output = Column(Text, nullable=True)
    parsed_output = Column(JSON, default=dict)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # LLM usage
    llm_model = Column(String, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    cost_estimate = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "session_id": str(self.session_id),
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "agent_type": self.agent_type.value if self.agent_type else None,
            "status": self.status.value if self.status else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
            "input_data": self.input_data or {},
            "raw_output": self.raw_output,
            "parsed_output": self.parsed_output or {},
            "error_message": self.error_message,
            "retry_count": self.retry_count,
            "llm_model": self.llm_model,
            "tokens_used": self.tokens_used,
            "cost_estimate": self.cost_estimate,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
