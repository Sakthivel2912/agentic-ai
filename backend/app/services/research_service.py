"""
AI Council - Research Service (SQLite)
"""
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import HTTPException, status
from sqlalchemy import select, or_, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.research_session import ResearchSession, SessionStatus, ResearchCategory
from app.schemas.research import ResearchSessionCreate, ResearchSessionUpdate, ResearchSessionResponse
from app.core.config import settings
from app.core.logging import setup_logging
import logging
import uuid

logger = logging.getLogger(__name__)


class ResearchService:
    """Research session service (SQLite)"""
    
    @staticmethod
    async def create_session(user_id: str, session_data: ResearchSessionCreate, db: AsyncSession) -> ResearchSessionResponse:
        """
        Create a new research session
        
        Args:
            user_id: User ID
            session_data: Session creation data
            db: Database session
            
        Returns:
            Created session response
        """
        try:
            session = ResearchSession(
                id=str(uuid.uuid4()),
                user_id=user_id,
                title=session_data.title,
                question=session_data.question,
                category=session_data.category,
                priority=session_data.priority,
                selected_agents=session_data.selected_agents,
                selected_document_ids=session_data.selected_document_ids,
                enable_rag=session_data.enable_rag,
                enable_review=session_data.enable_review,
                enable_citations=session_data.enable_citations,
                status=SessionStatus.DRAFT,
                progress=0.0,
                session_metadata={}
            )
            
            db.add(session)
            await db.commit()
            await db.refresh(session)
            
            logger.info(f"Research session created: {session.id}")
            return ResearchSessionResponse(**session.to_dict())
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating research session: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create research session"
            )
    
    @staticmethod
    async def get_session(session_id: str, user_id: str, db: AsyncSession) -> ResearchSessionResponse:
        """
        Get a research session by ID
        
        Args:
            session_id: Session ID
            user_id: User ID (for ownership check)
            db: Database session
            
        Returns:
            Session response
            
        Raises:
            HTTPException: If session not found or user doesn't own it
        """
        result = await db.execute(
            select(ResearchSession).where(ResearchSession.id == session_id)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Research session not found"
            )
        
        # Check ownership
        if session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this session"
            )
        
        return ResearchSessionResponse(**session.to_dict())
    
    @staticmethod
    async def list_sessions(
        user_id: str,
        db: AsyncSession,
        status: Optional[SessionStatus] = None,
        category: Optional[ResearchCategory] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        List research sessions for a user
        
        Args:
            user_id: User ID
            status: Filter by status
            category: Filter by category
            page: Page number
            page_size: Items per page
            db: Database session
            
        Returns:
            Session list response
        """
        # Build query
        query = select(ResearchSession).where(ResearchSession.user_id == user_id)
        
        if status:
            query = query.where(ResearchSession.status == status)
        if category:
            query = query.where(ResearchSession.category == category)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Get sessions with pagination
        query = query.order_by(ResearchSession.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await db.execute(query)
        sessions = result.scalars().all()
        
        return {
            "sessions": [ResearchSessionResponse(**session.to_dict()) for session in sessions],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    
    @staticmethod
    async def update_session(
        session_id: str,
        user_id: str,
        update_data: ResearchSessionUpdate,
        db: AsyncSession
    ) -> ResearchSessionResponse:
        """
        Update a research session
        
        Args:
            session_id: Session ID
            user_id: User ID (for ownership check)
            update_data: Data to update
            db: Database session
            
        Returns:
            Updated session response
            
        Raises:
            HTTPException: If session not found or user doesn't own it
        """
        result = await db.execute(
            select(ResearchSession).where(ResearchSession.id == session_id)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Research session not found"
            )
        
        # Check ownership
        if session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this session"
            )
        
        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            if hasattr(session, field) and value is not None:
                setattr(session, field, value)
        
        session.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(session)
        
        logger.info(f"Research session updated: {session.id}")
        return ResearchSessionResponse(**session.to_dict())
    
    @staticmethod
    async def delete_session(session_id: str, user_id: str, db: AsyncSession) -> bool:
        """
        Delete a research session
        
        Args:
            session_id: Session ID
            user_id: User ID (for ownership check)
            db: Database session
            
        Returns:
            True if successful
            
        Raises:
            HTTPException: If session not found or user doesn't own it
        """
        result = await db.execute(
            select(ResearchSession).where(ResearchSession.id == session_id)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Research session not found"
            )
        
        # Check ownership
        if session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this session"
            )
        
        await db.delete(session)
        await db.commit()
        
        logger.info(f"Research session deleted: {session_id}")
        return True
    
    @staticmethod
    async def start_session(session_id: str, user_id: str, db: AsyncSession) -> ResearchSessionResponse:
        """
        Start a research session (trigger agent workflow)
        
        Args:
            session_id: Session ID
            user_id: User ID (for ownership check)
            db: Database session
            
        Returns:
            Updated session response
            
        Raises:
            HTTPException: If session not found or user doesn't own it
        """
        result = await db.execute(
            select(ResearchSession).where(ResearchSession.id == session_id)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Research session not found"
            )
        
        # Check ownership
        if session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to start this session"
            )
        
        # Update status to running
        session.status = SessionStatus.RUNNING
        session.started_at = datetime.utcnow()
        session.progress = 0.0
        session.current_stage = "initializing"
        await db.commit()
        await db.refresh(session)
        
        # Trigger agent workflow (this would be done by the agent execution service)
        # For now, just mark as running
        
        logger.info(f"Research session started: {session_id}")
        return ResearchSessionResponse(**session.to_dict())
    
    @staticmethod
    async def cancel_session(session_id: str, user_id: str, db: AsyncSession) -> ResearchSessionResponse:
        """
        Cancel a running research session
        
        Args:
            session_id: Session ID
            user_id: User ID (for ownership check)
            db: Database session
            
        Returns:
            Updated session response
            
        Raises:
            HTTPException: If session not found or user doesn't own it
        """
        result = await db.execute(
            select(ResearchSession).where(ResearchSession.id == session_id)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Research session not found"
            )
        
        # Check ownership
        if session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to cancel this session"
            )
        
        # Update status to cancelled
        session.status = SessionStatus.CANCELLED
        session.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(session)
        
        logger.info(f"Research session cancelled: {session_id}")
        return ResearchSessionResponse(**session.to_dict())
