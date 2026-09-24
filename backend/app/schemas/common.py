"""
AI Council - Common Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Any, Generic, TypeVar
from datetime import datetime


class SuccessResponse(BaseModel):
    """Standard success response"""
    success: bool = True
    message: str
    data: Optional[Any] = None
    request_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {},
                "request_id": "req_123456"
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    error: dict
    request_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid input data",
                    "details": {}
                },
                "request_id": "req_123456"
            }
        }


class PaginatedResponse(BaseModel):
    """Paginated response schema"""
    success: bool = True
    data: list
    pagination: dict
    message: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": [],
                "pagination": {
                    "page": 1,
                    "page_size": 20,
                    "total": 100,
                    "total_pages": 5
                },
                "message": "Data retrieved successfully"
            }
        }


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    
    @property
    def skip(self) -> int:
        """Calculate skip value for pagination"""
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """Get limit value for pagination"""
        return self.page_size
