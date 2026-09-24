"""
AI Council - Evaluation Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models.evaluation import EvaluationStatus


class EvaluationCreate(BaseModel):
    """Evaluation creation schema"""
    session_id: str = Field(..., description="Research session ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "507f1f77bcf86cd799439011"
            }
        }


class EvaluationUpdate(BaseModel):
    """Evaluation update schema"""
    overall_score: Optional[float] = Field(None, ge=0, le=10)
    relevance_score: Optional[float] = Field(None, ge=0, le=10)
    completeness_score: Optional[float] = Field(None, ge=0, le=10)
    accuracy_score: Optional[float] = Field(None, ge=0, le=10)
    clarity_score: Optional[float] = Field(None, ge=0, le=10)
    agent_scores: Optional[Dict[str, float]] = None
    user_feedback: Optional[str] = None
    reviewer_comments: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "overall_score": 8.5,
                "relevance_score": 9.0,
                "completeness_score": 8.0,
                "accuracy_score": 8.5,
                "clarity_score": 8.5,
                "agent_scores": {"research_agent": 9.0},
                "user_feedback": "Very comprehensive analysis"
            }
        }


class EvaluationResponse(BaseModel):
    """Evaluation response schema"""
    id: str
    session_id: str
    user_id: str
    status: str
    overall_score: Optional[float]
    relevance_score: Optional[float]
    completeness_score: Optional[float]
    accuracy_score: Optional[float]
    clarity_score: Optional[float]
    agent_scores: Dict[str, float]
    user_feedback: Optional[str]
    reviewer_comments: Optional[str]
    agent_count: Optional[int]
    total_duration: Optional[float]
    token_usage: Optional[int]
    cost_estimate: Optional[float]
    comparison_with_previous: Optional[Dict[str, Any]]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "session_id": "507f1f77bcf86cd799439012",
                "user_id": "507f1f77bcf86cd799439013",
                "status": "completed",
                "overall_score": 8.5,
                "relevance_score": 9.0,
                "completeness_score": 8.0,
                "accuracy_score": 8.5,
                "clarity_score": 8.5,
                "agent_scores": {},
                "user_feedback": "Very comprehensive analysis",
                "reviewer_comments": "Good quality report",
                "agent_count": 6,
                "total_duration": 300.0,
                "token_usage": 15000,
                "cost_estimate": 0.015,
                "comparison_with_previous": {},
                "error_message": None,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:10:00"
            }
        }


class EvaluationListResponse(BaseModel):
    """Evaluation list response schema"""
    evaluations: List[EvaluationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
