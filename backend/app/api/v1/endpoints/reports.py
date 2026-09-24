"""
AI Council - Reports API Endpoints
Endpoints for report generation and management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from app.schemas.report import (
    ReportCreate,
    ReportUpdate,
    ReportResponse,
    ReportListResponse
)
from app.schemas.common import SuccessResponse
from app.services.report_service import ReportService
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.report import ReportStatus
from app.core.logging import setup_logging
from app.database.sqlite import sqlite
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post(
    "/",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a report",
    description="Create a new report from a research session"
)
async def create_report(
    report_data: ReportCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new report"""
    try:
        db = sqlite.get_session()
        report = await ReportService.create_report(user_id=str(current_user.id), report_data=report_data, db=db)
        return SuccessResponse(
            message="Report created successfully", data={"report": report}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create report"
        )


@router.post(
    "/{report_id}/generate",
    response_model=SuccessResponse,
    summary="Generate report content",
    description="Generate report content from research session data"
)
async def generate_report(
    report_id: str,
    current_user: User = Depends(get_current_user)
):
    """Generate report content"""
    try:
        db = sqlite.get_session()
        report = await ReportService.generate_report(report_id=report_id, user_id=str(current_user.id), db=db)
        return SuccessResponse(
            message="Report generated successfully", data={"report": report}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate report"
        )


@router.get(
    "/",
    response_model=SuccessResponse,
    summary="List reports",
    description="List all reports for the authenticated user"
)
async def list_reports(
    status: Optional[ReportStatus] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user)
):
    """List reports"""
    try:
        db = sqlite.get_session()
        result = await ReportService.list_reports(user_id=str(current_user.id), db=db, status=status, page=page, page_size=page_size)
        return SuccessResponse(
            message="Reports retrieved successfully", data=result
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing reports: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list reports"
        )


@router.get(
    "/{report_id}",
    response_model=SuccessResponse,
    summary="Get a report by ID",
    description="Retrieve a specific report by its ID"
)
async def get_report(
    report_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a report by ID"""
    try:
        db = sqlite.get_session()
        report = await ReportService.get_report(report_id=report_id, user_id=str(current_user.id), db=db)
        return SuccessResponse(
            message="Report retrieved successfully", data={"report": report}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get report"
        )
