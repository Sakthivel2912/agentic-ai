"""
AI Council - Research Session Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.research_session import SessionStatus, ResearchCategory


class ResearchSessionCreate(BaseModel):
    """Research session creation schema"""
    title: str = Field(..., min_length=1, max_length=200)
    question: str = Field(..., min_length=1)
    category: ResearchCategory = Field(default=ResearchCategory.GENERAL)
    priority: str = Field(default="medium")
    selected_agents: List[str] = Field(default_factory=list)
    enable_rag: bool = Field(default=False)
    enable_review: bool = Field(default=True)
    enable_citations: bool = Field(default=True)
    selected_document_ids: List[str] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Microservices vs Monolith Analysis",
                "question": "What are the pros and cons of using microservices architecture for a startup?",
                "category": "software_architecture",
                "priority": "high",
                "selected_agents": ["research_agent", "technical_agent", "cost_agent"],
                "enable_rag": True,
                "enable_review": True,
                "enable_citations": True,
                "selected_document_ids": []
            }
        }


class ResearchSessionUpdate(BaseModel):
    """Research session update schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    question: Optional[str] = Field(None, min_length=1)
    category: Optional[ResearchCategory] = None
    priority: Optional[str] = None
    selected_agents: Optional[List[str]] = None
    enable_rag: Optional[bool] = None
    enable_review: Optional[bool] = None
    enable_citations: Optional[bool] = None
    selected_document_ids: Optional[List[str]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Updated Research Title",
                "priority": "high"
            }
        }


class ResearchSessionResponse(BaseModel):
    """Research session response schema"""
    id: str
    user_id: str
    title: str
    question: str
    category: str
    priority: str
    selected_agents: List[str] = Field(default_factory=list)
    enable_rag: bool = False
    enable_review: bool = True
    enable_citations: bool = False
    selected_document_ids: List[str] = Field(default_factory=list)
    status: str = "draft"
    current_stage: str = ""
    progress: float = 0.0
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    updated_at: datetime
    agent_outputs: Dict[str, Any] = Field(default_factory=dict)
    reviewer_feedback: Optional[Dict[str, Any]] = Field(default_factory=dict)
    final_answer: Optional[str] = None
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "user_id": "507f1f77bcf86cd799439012",
                "title": "Microservices Analysis",
                "question": "What are the pros and cons of microservices?",
                "category": "software_architecture",
                "priority": "high",
                "selected_agents": ["research_agent", "technical_agent"],
                "enable_rag": True,
                "enable_review": True,
                "enable_citations": True,
                "selected_document_ids": [],
                "status": "completed",
                "current_stage": "synthesis",
                "progress": 100.0,
                "created_at": "2024-01-01T00:00:00",
                "started_at": "2024-01-01T00:05:00",
                "completed_at": "2024-01-01T00:30:00",
                "updated_at": "2024-01-01T00:30:00",
                "agent_outputs": {},
                "reviewer_feedback": {},
                "final_answer": "Based on the analysis...",
                "sources": [],
                "error_message": None,
                "metadata": {}
            }
        }


class ResearchSessionListResponse(BaseModel):
    """Research session list response schema"""
    sessions: List[ResearchSessionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class SessionStartRequest(BaseModel):
    """Session start request schema"""
    session_id: str