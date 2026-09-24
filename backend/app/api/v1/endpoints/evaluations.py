"""
AI Council - Evaluations API Endpoints
Endpoints for research session evaluations
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from app.schemas.evaluation import (
    EvaluationCreate,
    EvaluationUpdate,
    EvaluationResponse,
    EvaluationListResponse
)
from app.schemas.common import SuccessResponse
from app.services.evaluation_service import EvaluationService
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.evaluation import EvaluationStatus
from app.core.logging import setup_logging
from app.database.sqlite import sqlite
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/evaluations", tags=["Evaluations"])


@router.post(
    "/",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an evaluation",
    description="Create a new evaluation for a research session"
)
async def create_evaluation(
    evaluation_data: EvaluationCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new evaluation"""
    try:
        db = sqlite.get_session()
        evaluation = await EvaluationService.create_evaluation(user_id=str(current_user.id), evaluation_data=evaluation_data, db=db)
        return SuccessResponse(
            message="Evaluation created successfully", data={"evaluation": evaluation}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating evaluation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create evaluation"
        )


@router.post(
    "/{evaluation_id}/run",
    response_model=SuccessResponse,
    summary="Run evaluation",
    description="Run evaluation on a research session"
)
async def run_evaluation(
    evaluation_id: str,
    current_user: User = Depends(get_current_user)
):
    """Run evaluation"""
    try:
        db = sqlite.get_session()
        evaluation = await EvaluationService.run_evaluation(evaluation_id=evaluation_id, user_id=str(current_user.id), db=db)
        return SuccessResponse(
            message="Evaluation completed successfully", data={"evaluation": evaluation}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running evaluation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to run evaluation"
        )


@router.get(
    "/",
    response_model=SuccessResponse,
    summary="List evaluations",
    description="List all evaluations for the authenticated user"
)
async def list_evaluations(
    status: Optional[EvaluationStatus] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user)
):
    """List evaluations"""
    try:
        db = sqlite.get_session()
        result = await EvaluationService.list_evaluations(user_id=str(current_user.id), db=db, status=status, page=page, page_size=page_size)
        return SuccessResponse(
            message="Evaluations retrieved successfully", data=result
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing evaluations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list evaluations"
        )


@router.get(
    "/{evaluation_id}",
    response_model=SuccessResponse,
    summary="Get an evaluation by ID",
    description="Retrieve a specific evaluation by its ID"
)
async def get_evaluation(
    evaluation_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get an evaluation by ID"""
    try:
        db = sqlite.get_session()
        evaluation = await EvaluationService.get_evaluation(evaluation_id=evaluation_id, user_id=str(current_user.id), db=db)
        return SuccessResponse(
            message="Evaluation retrieved successfully", data={"evaluation": evaluation}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting evaluation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get evaluation"
        )
