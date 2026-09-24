"""
AI Council - Agent Execution Schemas
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models.agent_execution import AgentStatus, AgentType


class AgentExecutionCreate(BaseModel):
    """Agent execution creation schema"""
    session_id: str = Field(..., description="Research session ID")
    agent_id: str = Field(..., description="Agent identifier")
    agent_name: str = Field(..., description="Human-readable agent name")
    agent_type: AgentType = Field(..., description="Agent type")
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Input data for the agent")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "507f1f77bcf86cd799439011",
                "agent_id": "research_agent",
                "agent_name": "Research Agent",
                "agent_type": "research_agent",
                "input_data": {"question": "What is the best approach?"}
            }
        }


class AgentExecutionUpdate(BaseModel):
    """Agent execution update schema"""
    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra={
            "example": {
                "status": "completed",
                "output_data": {"answer": "Based on analysis..."},
                "raw_output": "Based on analysis...",
                "structured_output": {"key_points": []}
            }
        }
    )

    status: Optional[AgentStatus] = None
    output_data: Optional[Dict[str, Any]] = None
    raw_output: Optional[str] = None
    structured_output: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    retry_count: Optional[int] = None
    tokens_used: Optional[int] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    cost_estimate: Optional[float] = None
    model_used: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
class AgentExecutionResponse(BaseModel):
    """Agent execution response schema"""
    id: str
    session_id: str
    agent_id: str
    agent_name: str
    agent_type: str
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: Optional[float]
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]]
    raw_output: Optional[str]
    structured_output: Optional[Dict[str, Any]]
    error_message: Optional[str]
    error_type: Optional[str]
    retry_count: int
    llm_model: Optional[str]
    tokens_used: Optional[int]
    prompt_tokens: Optional[int]
    completion_tokens: Optional[int]
    cost_estimate: Optional[float]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "session_id": "507f1f77bcf86cd799439012",
                "agent_id": "research_agent",
                "agent_name": "Research Agent",
                "agent_type": "research_agent",
                "status": "completed",
                "started_at": "2024-01-01T00:05:00",
                "completed_at": "2024-01-01T00:10:00",
                "duration_seconds": 300.0,
                "input_data": {"question": "What is the best approach?"},
                "output_data": {"answer": "Based on analysis..."},
                "raw_output": "Based on analysis...",
                "structured_output": {"key_points": []},
                "error_message": None,
                "error_type": None,
                "retry_count": 0,
                "llm_model": "llama3-70b-8192",
                "tokens_used": 1500,
                "prompt_tokens": 800,
                "completion_tokens": 700,
                "cost_estimate": 0.0015,
                "metadata": {},
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:10:00"
            }
        }


class AgentExecutionListResponse(BaseModel):
    """Agent execution list response schema"""
    executions: List[AgentExecutionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AgentExecutionStartRequest(BaseModel):
    """Agent execution start request schema"""
    session_id: str
    agent_id: str
    input_data: Dict[str, Any] = Field(default_factory=dict)


class AgentExecutionCompleteRequest(BaseModel):
    """Agent execution completion request schema"""
    output_data: Dict[str, Any]
    raw_output: Optional[str] = None
    structured_output: Optional[Dict[str, Any]] = None
    tokens_used: Optional[int] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    cost_estimate: Optional[float] = None
    llm_model: Optional[str] = None


class AgentExecutionFailRequest(BaseModel):
    """Agent execution failure request schema"""
    error_message: str
    error_type: Optional[str] = None
