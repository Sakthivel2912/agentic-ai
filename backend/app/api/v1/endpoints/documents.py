"""
AI Council - Document Management API Endpoints
Endpoints for document upload, management, and retrieval
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from typing import Optional
from app.schemas.document import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentListResponse,
    DocumentUploadResponse
)
from app.schemas.common import SuccessResponse
from app.services.document_service import DocumentService
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.document import DocumentStatus, DocumentType
from app.core.config import settings
from app.core.logging import setup_logging
from app.database.sqlite import sqlite
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post(
    "/upload",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a document",
    description="Upload a document (PDF, TXT, MD) for processing and indexing"
)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = None,
    author: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Upload a document
    
    Args:
        file: Uploaded file
        title: Optional document title
        author: Optional document author
        current_user: Authenticated user
        
    Returns:
        Created document information
    """
    try:
        db = sqlite.get_session()
        file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
        file_type_map = {'pdf': DocumentType.PDF, 'txt': DocumentType.TXT, 'md': DocumentType.MARKDOWN, 'docx': DocumentType.DOCX}
        if file_extension not in file_type_map:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported file type: {file_extension}")
        file_type = file_type_map[file_extension]
        content = await file.read()
        file_size = len(content)
        if file_size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE} bytes")
        document_data = DocumentCreate(filename=file.filename, file_type=file_type, file_size=file_size, title=title, author=author)
        document = await DocumentService.create_document(user_id=str(current_user.id), document_data=document_data, file_content=content, db=db)
        return SuccessResponse(
            message="Document uploaded successfully",
            data={"document_id": str(document.id), "filename": document.filename, "status": document.status}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload document"
        )


@router.get(
    "/",
    response_model=SuccessResponse,
    summary="List documents",
    description="List all documents for the authenticated user"
)
async def list_documents(
    status: Optional[DocumentStatus] = Query(None, description="Filter by status"),
    file_type: Optional[DocumentType] = Query(None, description="Filter by file type"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user)
):
    """
    List documents for the authenticated user
    
    Args:
        status: Optional status filter
        file_type: Optional file type filter
        page: Page number (default: 1)
        page_size: Items per page (default: 20, max: 100)
        current_user: Authenticated user
        
    Returns:
        Paginated list of documents
    """
    try:
        db = sqlite.get_session()
        result = await DocumentService.list_documents(user_id=str(current_user.id), db=db, status=status, file_type=file_type, page=page, page_size=page_size)
        return SuccessResponse(
            message="Documents retrieved successfully", data=result
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list documents"
        )


@router.get(
    "/{document_id}",
    response_model=SuccessResponse,
    summary="Get a document by ID",
    description="Retrieve a specific document by its ID"
)
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get a document by ID
    
    Args:
        document_id: Document ID
        current_user: Authenticated user
        
    Returns:
        Document details
    """
    try:
        db = sqlite.get_session()
        document = await DocumentService.get_document(document_id=document_id, user_id=str(current_user.id), db=db)
        return SuccessResponse(
            message="Document retrieved successfully", data={"document": document}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get document"
        )


@router.put(
    "/{document_id}",
    response_model=SuccessResponse,
    summary="Update a document",
    description="Update document metadata"
)
async def update_document(
    document_id: str,
    update_data: DocumentUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update a document
    
    Args:
        document_id: Document ID
        update_data: Data to update
        current_user: Authenticated user
        
    Returns:
        Updated document
    """
    try:
        db = sqlite.get_session()
        document = await DocumentService.update_document(document_id=document_id, user_id=str(current_user.id), update_data=update_data, db=db)
        return SuccessResponse(
            message="Document updated successfully", data={"document": document}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update document"
        )


@router.delete(
    "/{document_id}",
    response_model=SuccessResponse,
    summary="Delete a document",
    description="Delete a document permanently"
)
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a document
    
    Args:
        document_id: Document ID
        current_user: Authenticated user
        
    Returns:
        Success message
    """
    try:
        db = sqlite.get_session()
        await DocumentService.delete_document(document_id=document_id, user_id=str(current_user.id), db=db)
        return SuccessResponse(
            message="Document deleted successfully", data={}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document"
        )


@router.post(
    "/{document_id}/reindex",
    response_model=SuccessResponse,
    summary="Re-index a document",
    description="Re-process and re-index a document"
)
async def reindex_document(
    document_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Re-index a document
    
    Args:
        document_id: Document ID
        current_user: Authenticated user
        
    Returns:
        Updated document
    """
    try:
        db = sqlite.get_session()
        document = await DocumentService.reindex_document(document_id=document_id, user_id=str(current_user.id), db=db)
        return SuccessResponse(
            message="Document re-indexing started", data={"document": document}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error re-indexing document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to re-index document"
        )
