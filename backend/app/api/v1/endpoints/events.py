"""
AI Council - Real-Time Events API Endpoints
SSE endpoints for real-time progress updates and event streaming
"""
from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse
from app.services.sse_service import sse_service
from app.core.logging import setup_logging
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/events", tags=["Real-Time Events"])


@router.get("/sessions/{session_id}/stream")
async def session_events_stream(request: Request, session_id: str):
    """
    SSE endpoint for real-time session events
    
    Args:
        request: FastAPI request
        session_id: Research session ID
        
    Returns:
        SSE event stream
    """
    # Register client connection
    queue = await sse_service.connect(session_id)
    
    # Create event generator
    event_generator = sse_service.event_generator(session_id, queue)
    
    # Return SSE response
    return EventSourceResponse(
        event_generator,
        media_type="text/event-stream",
    )
