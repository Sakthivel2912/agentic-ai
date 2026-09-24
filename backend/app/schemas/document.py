"""
AI Council - Document Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models.document import DocumentStatus, DocumentType


class DocumentCreate(BaseModel):
    """Document creation schema (metadata only)"""
    filename: str = Field(..., description="Original filename")
    file_type: DocumentType = Field(..., description="Document type")
    file_size: int = Field(..., description="File size in bytes")
    title: Optional[str] = Field(None, description="Document title")
    author: Optional[str] = Field(None, description="Document author")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "filename": "research_paper.pdf",
                "file_type": "pdf",
                "file_size": 1048576,
                "title": "Research Paper",
                "author": "John Doe",
                "metadata": {}
            }
        }


class DocumentUpdate(BaseModel):
    """Document update schema"""
    title: Optional[str] = None
    author: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Updated Title",
                "author": "Jane Doe"
            }
        }


class DocumentResponse(BaseModel):
    """Document response schema"""
    id: str
    user_id: str
    filename: str
    file_type: str
    file_size: int
    status: str
    progress: float
    extracted_text: Optional[str]
    chunk_count: Optional[int]
    chunks: List[Dict[str, Any]]
    embedding_model: Optional[str]
    embedding_dimension: Optional[int]
    pinecone_indexed: bool
    pinecone_id: Optional[str]
    title: Optional[str]
    author: Optional[str]
    created_date: Optional[datetime]
    metadata: Dict[str, Any]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "user_id": "507f1f77bcf86cd799439012",
                "filename": "research_paper.pdf",
                "file_type": "pdf",
                "file_size": 1048576,
                "status": "indexed",
                "progress": 100.0,
                "extracted_text": "Extracted text content...",
                "chunk_count": 25,
                "chunks": [],
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
                "embedding_dimension": 384,
                "pinecone_indexed": True,
                "pinecone_id": "vector-123",
                "title": "Research Paper",
                "author": "John Doe",
                "created_date": "2024-01-01T00:00:00",
                "metadata": {},
                "error_message": None,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:10:00"
            }
        }


class DocumentListResponse(BaseModel):
    """Document list response schema"""
    documents: List[DocumentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class DocumentUploadResponse(BaseModel):
    """Document upload response schema"""
    document_id: str
    filename: str
    status: str
    message: str


class RAGQueryRequest(BaseModel):
    """RAG query request schema"""
    query: str = Field(..., min_length=1, description="Query text")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of results to retrieve")
    session_id: Optional[str] = Field(None, description="Research session ID for context")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What are the benefits of microservices?",
                "top_k": 5,
                "session_id": "507f1f77bcf86cd799439011"
            }
        }


class RAGQueryResponse(BaseModel):
    """RAG query response schema"""
    query: str
    results: List[Dict[str, Any]]
    total_results: int
    query_embedding: Optional[List[float]]
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What are the benefits of microservices?",
                "results": [
                    {
                        "content": "Microservices offer scalability...",
                        "score": 0.95,
                        "document_id": "507f1f77bcf86cd799439011",
                        "document_title": "Microservices Architecture",
                        "chunk_index": 5
                    }
                ],
                "total_results": 5,
                "query_embedding": None
            }
        }
