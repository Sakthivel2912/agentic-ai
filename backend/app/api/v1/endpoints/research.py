"""
AI Council - Research Session API Endpoints
"""
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status, Query
from datetime import datetime
from sqlalchemy import select
from typing import Optional
from app.schemas.research import (
    ResearchSessionCreate,
    ResearchSessionUpdate,
    ResearchSessionResponse,
    ResearchSessionListResponse,
    SessionStartRequest
)
from app.schemas.common import SuccessResponse, ErrorResponse
from app.services.research_service import ResearchService
from app.services.sse_service import sse_service
from app.workflows.research_workflow import research_workflow
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.research_session import ResearchSession, SessionStatus, ResearchCategory
from app.database.sqlite import sqlite
from app.core.logging import setup_logging
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/research", tags=["Research Sessions"])


async def run_research_workflow(session_id: str, user_id: str) -> None:
    """Run a started session and persist its workflow results."""
    try:
        async with sqlite.get_session() as db:
            result = await db.execute(
                select(ResearchSession).where(
                    ResearchSession.id == session_id,
                    ResearchSession.user_id == user_id,
                )
            )
            session = result.scalar_one_or_none()
            if not session:
                return

            session.current_stage = "research_analysis"
            session.progress = 5.0
            await db.commit()
            await sse_service.send_progress_update(
                session_id, session.progress, session.current_stage
            )

            final_state = await research_workflow.execute_workflow(
                session_id=session.id,
                user_id=session.user_id,
                question=session.question,
                title=session.title,
                category=session.category.value if session.category else "general",
                selected_agents=session.selected_agents or [],
                enable_rag=session.enable_rag,
                enable_review=session.enable_review,
                enable_citations=session.enable_citations,
                selected_document_ids=session.selected_document_ids or [],
            )

            session.agent_outputs = final_state.get("agent_outputs", {})
            session.selected_agents = final_state.get("selected_agents", session.selected_agents or [])
            session.session_metadata = {
                **(session.session_metadata or {}),
                **(final_state.get("metadata") or {}),
            }
            session.reviewer_feedback = final_state.get("reviewer_feedback") or {}
            session.final_answer = final_state.get("final_answer")
            session.sources = final_state.get("sources", [])
            session.current_stage = final_state.get("current_stage", "completed")
            session.progress = final_state.get("progress", 100.0)
            session.error_message = final_state.get("error_message")
            session.status = (
                SessionStatus.FAILED
                if session.error_message
                else SessionStatus.COMPLETED
            )
            session.completed_at = datetime.utcnow()
            await db.commit()

            if session.error_message:
                await sse_service.send_error(session.id, session.error_message)
            else:
                await sse_service.send_progress_update(
                    session.id, session.progress, session.current_stage
                )
                await sse_service.send_completion(session.id, session.final_answer)
    except Exception as exc:
        logger.exception("Research workflow failed for session %s", session_id)
        await sse_service.send_error(session_id, str(exc), "workflow_error")


@router.post(
    "/sessions",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new research session",
    description="Create a new research session with the specified parameters"
)
async def create_research_session(
    session_data: ResearchSessionCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new research session
    
    Args:
        session_data: Research session creation data
        current_user: Authenticated user
        
    Returns:
        Created research session
    """
    try:
        async with sqlite.get_session() as db:
            session = await ResearchService.create_session(
                user_id=str(current_user.id),
                session_data=session_data,
                db=db
            )
            return SuccessResponse(
                message="Research session created successfully",
                data={"session": session}
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in create_research_session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create research session"
        )


@router.get(
    "/sessions/{session_id}",
    response_model=SuccessResponse,
    summary="Get a research session by ID",
    description="Retrieve a specific research session by its ID"
)
async def get_research_session(
    session_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Get a research session by ID
    
    Args:
        session_id: Research session ID
        current_user: Authenticated user
        
    Returns:
        Research session details
    """
    try:
        async with sqlite.get_session() as db:
            session = await ResearchService.get_session(
                session_id=session_id,
                user_id=str(current_user.id),
                db=db
            )
            if (
                session.status == SessionStatus.RUNNING
                and session.progress <= 0
                and session.current_stage == "initializing"
            ):
                background_tasks.add_task(
                    run_research_workflow,
                    session_id,
                    str(current_user.id),
                )
            return SuccessResponse(
                message="Research session retrieved successfully",
                data={"session": session}
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_research_session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get research session"
        )


@router.get(
    "/sessions",
    response_model=SuccessResponse,
    summary="List research sessions",
    description="List all research sessions for the authenticated user with optional filters"
)
async def list_research_sessions(
    status: Optional[SessionStatus] = Query(None, description="Filter by session status"),
    category: Optional[ResearchCategory] = Query(None, description="Filter by research category"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user)
):
    """
    List research sessions for the authenticated user
    
    Args:
        status: Optional status filter
        category: Optional category filter
        page: Page number (default: 1)
        page_size: Items per page (default: 20, max: 100)
        current_user: Authenticated user
        
    Returns:
        Paginated list of research sessions
    """
    try:
        db = sqlite.get_session()
        result = await ResearchService.list_sessions(
            user_id=str(current_user.id),
            db=db,
            status=status,
            category=category,
            page=page,
            page_size=page_size
        )
        return SuccessResponse(
            message="Research sessions retrieved successfully",
            data=result
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in list_research_sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list research sessions"
        )


@router.put(
    "/sessions/{session_id}",
    response_model=SuccessResponse,
    summary="Update a research session",
    description="Update an existing research session"
)
async def update_research_session(
    session_id: str,
    update_data: ResearchSessionUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update a research session
    
    Args:
        session_id: Research session ID
        update_data: Data to update
        current_user: Authenticated user
        
    Returns:
        Updated research session
    """
    try:
        db = sqlite.get_session()
        session = await ResearchService.update_session(
            session_id=session_id,
            user_id=str(current_user.id),
            update_data=update_data,
            db=db
        )
        return SuccessResponse(
            message="Research session updated successfully",
            data={"session": session}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_research_session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update research session"
        )


@router.delete(
    "/sessions/{session_id}",
    response_model=SuccessResponse,
    summary="Delete a research session",
    description="Delete a research session permanently"
)
async def delete_research_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a research session
    
    Args:
        session_id: Research session ID
        current_user: Authenticated user
        
    Returns:
        Success message
    """
    try:
        db = sqlite.get_session()
        await ResearchService.delete_session(
            session_id=session_id,
            user_id=str(current_user.id),
            db=db
        )
        return SuccessResponse(
            message="Research session deleted successfully",
            data={}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in delete_research_session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete research session"
        )


@router.post(
    "/sessions/{session_id}/start",
    response_model=SuccessResponse,
    summary="Start a research session",
    description="Start execution of a research session"
)
async def start_research_session(
    session_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Start a research session
    
    Args:
        session_id: Research session ID
        current_user: Authenticated user
        
    Returns:
        Updated research session with running status
    """
    try:
        async with sqlite.get_session() as db:
            session = await ResearchService.start_session(
                session_id=session_id,
                user_id=str(current_user.id),
                db=db
            )
        background_tasks.add_task(
            run_research_workflow,
            session_id,
            str(current_user.id),
        )
        return SuccessResponse(
            message="Research session started successfully",
            data={"session": session}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in start_research_session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start research session"
        )


@router.post(
    "/sessions/{session_id}/cancel",
    response_model=SuccessResponse,
    summary="Cancel a research session",
    description="Cancel an active research session"
)
async def cancel_research_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Cancel a research session
    
    Args:
        session_id: Research session ID
        current_user: Authenticated user
        
    Returns:
        Updated research session with cancelled status
    """
    try:
        db = sqlite.get_session()
        session = await ResearchService.cancel_session(
            session_id=session_id,
            user_id=str(current_user.id),
            db=db
        )
        return SuccessResponse(
            message="Research session cancelled successfully",
            data={"session": session}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in cancel_research_session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel research session"
        )
