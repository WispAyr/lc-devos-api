"""Cost tracking endpoints - BeanCounter data."""
from datetime import date
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.database import get_db
from src.models.cost import CostRecord
from src.models.project import Project
from src.schemas.cost import CostRecordResponse, CostSummary

router = APIRouter(prefix="/costs", tags=["costs"])


@router.get("", response_model=list[CostRecordResponse])
async def list_cost_records(
    project_id: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(100, le=500),
    db: AsyncSession = Depends(get_db)
):
    """List cost records with filtering."""
    query = select(CostRecord)

    if project_id:
        query = query.where(CostRecord.project_id == project_id)
    if start_date:
        query = query.where(CostRecord.record_date >= start_date)
    if end_date:
        query = query.where(CostRecord.record_date <= end_date)

    query = query.order_by(CostRecord.created_at.desc()).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/summary/{project_id}", response_model=CostSummary)
async def get_cost_summary(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get cost summary for a project."""
    today = date.today()

    # Get project for budget info
    project_result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = project_result.scalar_one_or_none()

    # Get today's costs
    today_result = await db.execute(
        select(
            func.sum(CostRecord.total_tokens).label("tokens"),
            func.sum(CostRecord.estimated_cost_cents).label("cost")
        )
        .where(CostRecord.project_id == project_id)
        .where(CostRecord.record_date == today)
    )
    today_row = today_result.one()

    # Get all-time costs
    total_result = await db.execute(
        select(
            func.sum(CostRecord.total_tokens).label("tokens"),
            func.sum(CostRecord.estimated_cost_cents).label("cost")
        )
        .where(CostRecord.project_id == project_id)
    )
    total_row = total_result.one()

    tokens_today = today_row.tokens or 0
    cost_today = today_row.cost or 0
    tokens_total = total_row.tokens or 0
    cost_total = total_row.cost or 0

    budget_remaining = None
    budget_percentage = None
    if project and project.daily_token_budget:
        budget_remaining = project.daily_token_budget - tokens_today
        budget_percentage = (tokens_today / project.daily_token_budget) * 100

    return CostSummary(
        project_id=project_id,
        total_tokens_today=tokens_today,
        total_tokens_all_time=tokens_total,
        estimated_cost_today_cents=cost_today,
        estimated_cost_all_time_cents=cost_total,
        daily_token_budget=project.daily_token_budget if project else None,
        budget_remaining_today=budget_remaining,
        budget_percentage_used=budget_percentage
    )


@router.get("/today", response_model=list[CostRecordResponse])
async def get_today_costs(db: AsyncSession = Depends(get_db)):
    """Get all cost records for today."""
    today = date.today()
    result = await db.execute(
        select(CostRecord)
        .where(CostRecord.record_date == today)
        .order_by(CostRecord.created_at.desc())
    )
    return result.scalars().all()
