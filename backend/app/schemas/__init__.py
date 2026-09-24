"""
AI Council - Schemas Package
"""
from app.schemas.user import (
    UserRegister,
    UserLogin,
    UserResponse,
    UserUpdate,
    PasswordChange,
    TokenResponse
)
from app.schemas.common import (
    SuccessResponse,
    ErrorResponse,
    PaginatedResponse,
    PaginationParams
)
from app.schemas.research import (
    ResearchSessionCreate,
    ResearchSessionUpdate,
    ResearchSessionResponse,
    ResearchSessionListResponse,
    SessionStartRequest
)
from app.schemas.agent import (
    AgentExecutionCreate,
    AgentExecutionUpdate,
    AgentExecutionResponse,
    AgentExecutionListResponse,
    AgentExecutionStartRequest,
    AgentExecutionCompleteRequest,
    AgentExecutionFailRequest
)
from app.schemas.document import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentListResponse,
    DocumentUploadResponse,
    RAGQueryRequest,
    RAGQueryResponse
)
from app.schemas.report import (
    ReportCreate,
    ReportUpdate,
    ReportResponse,
    ReportListResponse
)
from app.schemas.evaluation import (
    EvaluationCreate,
    EvaluationUpdate,
    EvaluationResponse,
    EvaluationListResponse
)

__all__ = [
    "UserRegister",
    "UserLogin",
    "UserResponse",
    "UserUpdate",
    "PasswordChange",
    "TokenResponse",
    "SuccessResponse",
    "ErrorResponse",
    "PaginatedResponse",
    "PaginationParams",
    "ResearchSessionCreate",
    "ResearchSessionUpdate",
    "ResearchSessionResponse",
    "ResearchSessionListResponse",
    "SessionStartRequest",
    "AgentExecutionCreate",
    "AgentExecutionUpdate",
    "AgentExecutionResponse",
    "AgentExecutionListResponse",
    "AgentExecutionStartRequest",
    "AgentExecutionCompleteRequest",
    "AgentExecutionFailRequest",
    "DocumentCreate",
    "DocumentUpdate",
    "DocumentResponse",
    "DocumentListResponse",
    "DocumentUploadResponse",
    "RAGQueryRequest",
    "RAGQueryResponse",
    "ReportCreate",
    "ReportUpdate",
    "ReportResponse",
    "ReportListResponse",
    "EvaluationCreate",
    "EvaluationUpdate",
    "EvaluationResponse",
    "EvaluationListResponse"
]
