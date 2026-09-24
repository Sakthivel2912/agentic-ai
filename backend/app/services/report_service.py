"""
AI Council - Report Service (SQLite - Stub)
"""
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.report import Report, ReportStatus
from app.models.research_session import ResearchSession
from app.schemas.report import ReportCreate, ReportResponse
from app.core.logging import setup_logging
import logging
import uuid

logger = logging.getLogger(__name__)


class ReportService:
    """Report service (SQLite - Stub)"""
    
    @staticmethod
    async def create_report(
        user_id: str,
        report_data: ReportCreate,
        db: AsyncSession
    ) -> ReportResponse:
        """Create a new report"""
        result = await db.execute(
            select(ResearchSession).where(ResearchSession.id == report_data.session_id)
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
                detail="You don't have permission to create a report for this session"
            )
        
        report = Report(
            id=str(uuid.uuid4()),
            session_id=session.id,
            user_id=user_id,
            title=report_data.title,
            format=report_data.format,
            status=ReportStatus.DRAFT
        )
        
        db.add(report)
        await db.commit()
        await db.refresh(report)
        
        return ReportResponse(**report.to_dict())
    
    @staticmethod
    async def generate_report(report_id: str, user_id: str, db: AsyncSession) -> ReportResponse:
        """Generate report content (stub)"""
        result = await db.execute(
            select(Report).where(Report.id == report_id)
        )
        report = result.scalar_one_or_none()
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        if report.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to generate this report"
            )
        
        # Stub: Generate placeholder content
        report.content = f"# {report.title}\n\nGenerated report content (stub implementation)"
        report.status = ReportStatus.COMPLETED
        report.word_count = len(report.content.split())
        report.character_count = len(report.content)
        
        await db.commit()
        await db.refresh(report)
        
        return ReportResponse(**report.to_dict())
    
    @staticmethod
    async def get_report(report_id: str, user_id: str, db: AsyncSession) -> ReportResponse:
        """Get a report by ID"""
        result = await db.execute(
            select(Report).where(Report.id == report_id)
        )
        report = result.scalar_one_or_none()
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        if report.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this report"
            )
        
        return ReportResponse(**report.to_dict())
    
    @staticmethod
    async def list_reports(
        user_id: str,
        db: AsyncSession,
        status: Optional[ReportStatus] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """List reports for a user"""
        from sqlalchemy import func
        
        query = select(Report).where(Report.user_id == user_id)
        
        if status:
            query = query.where(Report.status == status)
        
        total_result = await db.execute(select(func.count()).select_from(query.subquery()))
        total = total_result.scalar()
        
        query = query.order_by(Report.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await db.execute(query)
        reports = result.scalars().all()
        
        return {
            "reports": [ReportResponse(**report.to_dict()) for report in reports],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
