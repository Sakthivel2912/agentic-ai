"""
AI Council - Evaluation Service (SQLite - Stub)
"""
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.evaluation import Evaluation, EvaluationStatus
from app.models.research_session import ResearchSession
from app.schemas.evaluation import EvaluationCreate, EvaluationResponse
from app.core.logging import setup_logging
import logging
import uuid

logger = logging.getLogger(__name__)


class EvaluationService:
    """Evaluation service (SQLite - Stub)"""
    
    @staticmethod
    async def create_evaluation(
        user_id: str,
        evaluation_data: EvaluationCreate,
        db: AsyncSession
    ) -> EvaluationResponse:
        """Create a new evaluation"""
        result = await db.execute(
            select(ResearchSession).where(ResearchSession.id == evaluation_data.session_id)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Research session not found"
            )
        
        if session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to evaluate this session"
            )
        
        evaluation = Evaluation(
            id=str(uuid.uuid4()),
            session_id=session.id,
            user_id=user_id,
            status=EvaluationStatus.PENDING
        )
        
        db.add(evaluation)
        await db.commit()
        await db.refresh(evaluation)
        
        return EvaluationResponse(**evaluation.to_dict())
    
    @staticmethod
    async def run_evaluation(evaluation_id: str, user_id: str, db: AsyncSession) -> EvaluationResponse:
        """Run evaluation on a research session (stub)"""
        result = await db.execute(
            select(Evaluation).where(Evaluation.id == evaluation_id)
        )
        evaluation = result.scalar_one_or_none()
        
        if not evaluation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evaluation not found"
            )
        
        if evaluation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to run this evaluation"
            )
        
        # Stub: Set placeholder scores
        evaluation.status = EvaluationStatus.COMPLETED
        evaluation.overall_score = 7.5
        evaluation.relevance_score = 8.0
        evaluation.completeness_score = 7.0
        evaluation.accuracy_score = 7.5
        evaluation.clarity_score = 7.5
        evaluation.agent_scores = {"research_agent": 8.0, "technical_agent": 7.5}
        evaluation.agent_count = 3
        evaluation.total_duration = 60.0
        evaluation.token_usage = 500
        evaluation.cost_estimate = 0.005
        
        await db.commit()
        await db.refresh(evaluation)
        
        return EvaluationResponse(**evaluation.to_dict())
    
    @staticmethod
    async def get_evaluation(evaluation_id: str, user_id: str, db: AsyncSession) -> EvaluationResponse:
        """Get an evaluation by ID"""
        result = await db.execute(
            select(Evaluation).where(Evaluation.id == evaluation_id)
        )
        evaluation = result.scalar_one_or_none()
        
        if not evaluation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evaluation not found"
            )
        
        if evaluation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this evaluation"
            )
        
        return EvaluationResponse(**evaluation.to_dict())
    
    @staticmethod
    async def list_evaluations(
        user_id: str,
        db: AsyncSession,
        status: Optional[EvaluationStatus] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """List evaluations for a user"""
        query = select(Evaluation).where(Evaluation.user_id == user_id)
        
        if status:
            query = query.where(Evaluation.status == status)
        
        total_result = await db.execute(select(func.count()).select_from(query.subquery()))
        total = total_result.scalar()
        
        query = query.order_by(Evaluation.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await db.execute(query)
        evaluations = result.scalars().all()
        
        return {
            "evaluations": [EvaluationResponse(**eval.to_dict()) for eval in evaluations],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
