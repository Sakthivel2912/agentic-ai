"""
AI Council - Report Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models.report import ReportStatus, ReportFormat


class ReportCreate(BaseModel):
    """Report creation schema"""
    session_id: str = Field(..., description="Research session ID")
    title: str = Field(..., description="Report title")
    format: ReportFormat = Field(default=ReportFormat.MARKDOWN, description="Report format")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "507f1f77bcf86cd799439011",
                "title": "Microservices Analysis Report",
                "format": "markdown"
            }
        }


class ReportUpdate(BaseModel):
    """Report update schema"""
    title: Optional[str] = None
    content: Optional[str] = None
    sections: Optional[List[Dict[str, Any]]] = None
    sources: Optional[List[Dict[str, Any]]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Updated Title",
                "content": "Updated content..."
            }
        }


class ReportResponse(BaseModel):
    """Report response schema"""
    id: str
    session_id: str
    user_id: str
    title: str
    content: Optional[str]
    html_content: Optional[str]
    json_content: Optional[Dict[str, Any]]
    status: str
    format: str
    sections: List[Dict[str, Any]]
    sources: List[Dict[str, Any]]
    word_count: Optional[int]
    character_count: Optional[int]
    export_path: Optional[str]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "session_id": "507f1f77bcf86cd799439012",
                "user_id": "507f1f77bcf86cd799439013",
                "title": "Microservices Analysis Report",
                "content": "# Microservices Analysis\n\n## Executive Summary...",
                "html_content": "<h1>Microservices Analysis</h1>...",
                "json_content": {},
                "status": "completed",
                "format": "markdown",
                "sections": [],
                "sources": [],
                "word_count": 2500,
                "character_count": 15000,
                "export_path": "/reports/microservices_analysis.pdf",
                "error_message": None,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:10:00"
            }
        }


class ReportListResponse(BaseModel):
    """Report list response schema"""
    reports: List[ReportResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
