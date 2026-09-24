"""
AI Council - Document Service (SQLite)
"""
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.document import Document, DocumentStatus, DocumentType
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentResponse
from app.core.config import settings
from app.core.logging import setup_logging
import logging
import uuid

logger = logging.getLogger(__name__)


class DocumentService:
    """Document service (SQLite)"""
    
    @staticmethod
    async def create_document(
        user_id: str,
        document_data: DocumentCreate,
        file_content: bytes,
        db: AsyncSession
    ) -> DocumentResponse:
        """Create a new document"""
        try:
            document = Document(
                id=str(uuid.uuid4()),
                user_id=user_id,
                filename=document_data.filename,
                file_type=document_data.file_type,
                file_size=document_data.file_size,
                title=document_data.title,
                author=document_data.author,
                doc_metadata=document_data.metadata,
                status=DocumentStatus.UPLOADED,
                progress=0.0
            )
            
            db.add(document)
            await db.commit()
            await db.refresh(document)
            
            logger.info(f"Document created: {document.id}")
            return DocumentResponse(**document.to_dict())
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating document: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create document"
            )
    
    @staticmethod
    async def get_document(document_id: str, user_id: str, db: AsyncSession) -> DocumentResponse:
        """Get a document by ID"""
        result = await db.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        if document.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this document"
            )
        
        return DocumentResponse(**document.to_dict())
    
    @staticmethod
    async def list_documents(
        user_id: str,
        db: AsyncSession,
        status: Optional[DocumentStatus] = None,
        file_type: Optional[DocumentType] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """List documents for a user"""
        query = select(Document).where(Document.user_id == user_id)
        
        if status:
            query = query.where(Document.status == status)
        if file_type:
            query = query.where(Document.file_type == file_type)
        
        total_result = await db.execute(select(func.count()).select_from(query.subquery()))
        total = total_result.scalar()
        
        query = query.order_by(Document.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await db.execute(query)
        documents = result.scalars().all()
        
        return {
            "documents": [DocumentResponse(**doc.to_dict()) for doc in documents],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    
    @staticmethod
    async def update_document(
        document_id: str,
        user_id: str,
        update_data: DocumentUpdate,
        db: AsyncSession
    ) -> DocumentResponse:
        """Update a document"""
        result = await db.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        if document.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this document"
            )
        
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            if hasattr(document, field) and value is not None:
                setattr(document, field, value)
        
        document.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(document)
        
        return DocumentResponse(**document.to_dict())
    
    @staticmethod
    async def delete_document(document_id: str, user_id: str, db: AsyncSession) -> bool:
        """Delete a document"""
        result = await db.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        if document.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this document"
            )
        
        await db.delete(document)
        await db.commit()
        
        logger.info(f"Document deleted: {document_id}")
        return True
    
    @staticmethod
    async def reindex_document(document_id: str, user_id: str, db: AsyncSession) -> DocumentResponse:
        """Re-process and re-index a document"""
        result = await db.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        if document.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to re-index this document"
            )
        
        document.status = DocumentStatus.UPLOADED
        document.progress = 0.0
        document.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(document)
        
        logger.info(f"Document re-indexing started: {document_id}")
        return DocumentResponse(**document.to_dict())
