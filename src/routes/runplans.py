"""RunPlan management endpoints."""
import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database import get_db
from src.models.runplan import RunPlan, RunPlanStatus
from src.schemas.runplan import RunPlanCreate, RunPlanUpdate, RunPlanResponse
from src.services.broadcaster import broadcast_runplan_update

router = APIRouter(prefix="/runplans", tags=["runplans"])


@router.get("", response_model=list[RunPlanResponse])
async def list_runplans(
    task_id: Optional[str] = Query(None),
    status: Optional[RunPlanStatus] = Query(None),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db)
):
    """List RunPlans with optional filtering."""
    query = select(RunPlan)

    if task_id:
        query = query.where(RunPlan.task_id == task_id)
    if status:
        query = query.where(RunPlan.status == status)

    query = query.limit(limit).order_by(RunPlan.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/active", response_model=list[RunPlanResponse])
async def list_active_runplans(db: AsyncSession = Depends(get_db)):
    """List currently running RunPlans."""
    result = await db.execute(
        select(RunPlan).where(RunPlan.status == RunPlanStatus.RUNNING)
    )
    return result.scalars().all()


@router.get("/{runplan_id}", response_model=RunPlanResponse)
async def get_runplan(runplan_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific RunPlan by ID."""
    result = await db.execute(select(RunPlan).where(RunPlan.id == runplan_id))
    runplan = result.scalar_one_or_none()
    if not runplan:
        raise HTTPException(status_code=404, detail="RunPlan not found")
    return runplan


@router.post("", response_model=RunPlanResponse)
async def create_runplan(
    runplan_data: RunPlanCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new RunPlan."""
    runplan = RunPlan(
        id=str(uuid.uuid4()),
        **runplan_data.model_dump()
    )
    db.add(runplan)
    await db.flush()
    await broadcast_runplan_update(runplan)
    return runplan


@router.patch("/{runplan_id}", response_model=RunPlanResponse)
async def update_runplan(
    runplan_id: str,
    runplan_data: RunPlanUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a RunPlan."""
    result = await db.execute(select(RunPlan).where(RunPlan.id == runplan_id))
    runplan = result.scalar_one_or_none()
    if not runplan:
        raise HTTPException(status_code=404, detail="RunPlan not found")

    update_data = runplan_data.model_dump(exclude_unset=True)

    # Track status transitions
    if "status" in update_data:
        new_status = update_data["status"]
        if new_status == RunPlanStatus.RUNNING and not runplan.started_at:
            runplan.started_at = datetime.utcnow()
        elif new_status in [RunPlanStatus.COMPLETED, RunPlanStatus.FAILED, RunPlanStatus.CANCELLED]:
            runplan.completed_at = datetime.utcnow()

    for field, value in update_data.items():
        setattr(runplan, field, value)

    await db.flush()
    await broadcast_runplan_update(runplan)
    return runplan


@router.post("/{runplan_id}/start", response_model=RunPlanResponse)
async def start_runplan(runplan_id: str, db: AsyncSession = Depends(get_db)):
    """Start executing a RunPlan."""
    result = await db.execute(select(RunPlan).where(RunPlan.id == runplan_id))
    runplan = result.scalar_one_or_none()
    if not runplan:
        raise HTTPException(status_code=404, detail="RunPlan not found")

    if runplan.status not in [RunPlanStatus.DRAFT, RunPlanStatus.PENDING]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot start RunPlan in {runplan.status} status"
        )

    runplan.status = RunPlanStatus.RUNNING
    runplan.started_at = datetime.utcnow()
    await db.flush()
    await broadcast_runplan_update(runplan)
    return runplan
