"""
AI Council - SSE (Server-Sent Events) Service
Service for broadcasting real-time events to connected clients
"""
from typing import Dict, Set, Any, Optional
from fastapi import Request
from sse_starlette.sse import EventSourceResponse
import asyncio
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class SSEService:
    """
    SSE Service for real-time event broadcasting
    Manages client connections and event distribution
    """
    
    def __init__(self):
        # Store connected clients: {session_id: Set[queues]}
        self.clients: Dict[str, Set[asyncio.Queue]] = {}
        # Lock for thread-safe operations
        self.lock = asyncio.Lock()
    
    async def connect(self, session_id: str) -> asyncio.Queue:
        """
        Register a new client connection for a session
        
        Args:
            session_id: Research session ID
            
        Returns:
            Queue for sending events to this client
        """
        async with self.lock:
            if session_id not in self.clients:
                self.clients[session_id] = set()
            
            queue = asyncio.Queue()
            self.clients[session_id].add(queue)
            
            logger.info(f"Client connected for session {session_id}. Total clients: {len(self.clients[session_id])}")
            return queue
    
    async def disconnect(self, session_id: str, queue: asyncio.Queue) -> None:
        """
        Remove a client connection
        
        Args:
            session_id: Research session ID
            queue: Client's event queue
        """
        async with self.lock:
            if session_id in self.clients:
                self.clients[session_id].discard(queue)
                
                if not self.clients[session_id]:
                    del self.clients[session_id]
                
                logger.info(f"Client disconnected for session {session_id}. Remaining clients: {len(self.clients.get(session_id, set()))}")
    
    async def broadcast(self, session_id: str, event_type: str, data: Dict[str, Any]) -> None:
        """
        Broadcast an event to all clients connected to a session
        
        Args:
            session_id: Research session ID
            event_type: Type of event (e.g., "progress", "agent_output", "error")
            data: Event data
        """
        async with self.lock:
            if session_id not in self.clients:
                return
            
            # Create event message
            event = {
                "type": event_type,
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Send to all connected clients
            for queue in self.clients[session_id]:
                try:
                    await queue.put(event)
                except Exception as e:
                    logger.error(f"Error sending event to client: {e}")
    
    async def send_progress_update(
        self,
        session_id: str,
        progress: float,
        current_stage: str,
        agent_id: Optional[str] = None
    ) -> None:
        """
        Send a progress update event
        
        Args:
            session_id: Research session ID
            progress: Progress percentage (0-100)
            current_stage: Current workflow stage
            agent_id: Currently executing agent (if any)
        """
        await self.broadcast(
            session_id=session_id,
            event_type="progress",
            data={
                "progress": progress,
                "current_stage": current_stage,
                "agent_id": agent_id
            }
        )
    
    async def send_agent_output(
        self,
        session_id: str,
        agent_id: str,
        output: Dict[str, Any]
    ) -> None:
        """
        Send an agent output event
        
        Args:
            session_id: Research session ID
            agent_id: Agent that produced the output
            output: Agent output data
        """
        await self.broadcast(
            session_id=session_id,
            event_type="agent_output",
            data={
                "agent_id": agent_id,
                "output": output
            }
        )
    
    async def send_error(
        self,
        session_id: str,
        error_message: str,
        error_type: Optional[str] = None
    ) -> None:
        """
        Send an error event
        
        Args:
            session_id: Research session ID
            error_message: Error message
            error_type: Error type
        """
        await self.broadcast(
            session_id=session_id,
            event_type="error",
            data={
                "error_message": error_message,
                "error_type": error_type
            }
        )
    
    async def send_completion(
        self,
        session_id: str,
        final_answer: Optional[str] = None
    ) -> None:
        """
        Send a completion event
        
        Args:
            session_id: Research session ID
            final_answer: Final synthesized answer
        """
        await self.broadcast(
            session_id=session_id,
            event_type="completion",
            data={
                "final_answer": final_answer
            }
        )
    
    async def event_generator(self, session_id: str, queue: asyncio.Queue):
        """
        Generate SSE events for a client
        
        Args:
            session_id: Research session ID
            queue: Client's event queue
            
        Yields:
            SSE event messages
        """
        try:
            while True:
                # Wait for event with timeout
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield {
                        "event": event["type"],
                        "data": json.dumps(event["data"])
                    }
                except asyncio.TimeoutError:
                    # Send keepalive
                    yield {
                        "event": "keepalive",
                        "data": json.dumps({"timestamp": datetime.utcnow().isoformat()})
                    }
        except asyncio.CancelledError:
            logger.info(f"Event generator cancelled for session {session_id}")
        finally:
            await self.disconnect(session_id, queue)


# Global SSE service instance
sse_service = SSEService()
