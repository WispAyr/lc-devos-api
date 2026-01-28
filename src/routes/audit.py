"""Audit log endpoints."""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database import get_db
from src.models.audit import AuditLog, AuditAction
from src.schemas.audit import AuditLogResponse

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=list[AuditLogResponse])
async def list_audit_logs(
    project_id: Optional[str] = Query(None),
    agent_id: Optional[str] = Query(None),
    task_id: Optional[str] = Query(None),
    action: Optional[AuditAction] = Query(None),
    limit: int = Query(100, le=1000),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db)
):
    """List audit logs with filtering."""
    query = select(AuditLog)

    if project_id:
        query = query.where(AuditLog.project_id == project_id)
    if agent_id:
        query = query.where(AuditLog.agent_id == agent_id)
    if task_id:
        query = query.where(AuditLog.task_id == task_id)
    if action:
        query = query.where(AuditLog.action == action)

    query = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/recent", response_model=list[AuditLogResponse])
async def get_recent_activity(
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db)
):
    """Get most recent activity across all agents."""
    result = await db.execute(
        select(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/agent/{agent_id}", response_model=list[AuditLogResponse])
async def get_agent_activity(
    agent_id: str,
    limit: int = Query(100, le=500),
    db: AsyncSession = Depends(get_db)
):
    """Get activity for a specific agent."""
    result = await db.execute(
        select(AuditLog)
        .where(AuditLog.agent_id == agent_id)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
    )
    return result.scalars().all()
