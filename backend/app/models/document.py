"""
AI Council - Document Model (SQLAlchemy)
"""
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, JSON, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.sql import func
from app.database.sqlite import Base
from enum import Enum


class DocumentStatus(str, Enum):
    """Document processing status"""
    UPLOADED = "uploaded"
    EXTRACTING = "extracting"
    EXTRACTED = "extracted"
    CHUNKING = "chunking"
    CHUNKED = "chunked"
    EMBEDDING = "embedding"
    EMBEDDED = "embedded"
    INDEXING = "indexing"
    INDEXED = "indexed"
    FAILED = "failed"


class DocumentType(str, Enum):
    """Document type enumeration"""
    PDF = "pdf"
    TXT = "txt"
    MARKDOWN = "md"
    DOCX = "docx"


class Document(Base):
    """
    Document Model (SQLAlchemy)
    """
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    filename = Column(String, nullable=False)
    file_type = Column(SQLEnum(DocumentType), nullable=False)
    file_size = Column(Integer, nullable=False)
    
    # Processing status
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.UPLOADED)
    progress = Column(Float, default=0.0)
    
    # Content
    extracted_text = Column(Text, nullable=True)
    chunk_count = Column(Integer, nullable=True)
    chunks = Column(JSON, default=list)
    
    # Embedding
    embedding_model = Column(String, nullable=True)
    embedding_dimension = Column(Integer, nullable=True)
    
    # Vector database
    pinecone_indexed = Column(Boolean, default=False)
    pinecone_id = Column(String, nullable=True)
    
    # Metadata
    title = Column(String, nullable=True)
    author = Column(String, nullable=True)
    created_date = Column(DateTime(timezone=True), nullable=True)
    doc_metadata = Column(JSON, default=dict)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "filename": self.filename,
            "file_type": self.file_type.value if self.file_type else None,
            "file_size": self.file_size,
            "status": self.status.value if self.status else None,
            "progress": self.progress,
            "extracted_text": self.extracted_text,
            "chunk_count": self.chunk_count,
            "chunks": self.chunks or [],
            "embedding_model": self.embedding_model,
            "embedding_dimension": self.embedding_dimension,
            "pinecone_indexed": self.pinecone_indexed,
            "pinecone_id": self.pinecone_id,
            "title": self.title,
            "author": self.author,
            "created_date": self.created_date.isoformat() if self.created_date else None,
            "metadata": self.doc_metadata or {},
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
