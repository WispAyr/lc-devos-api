"""Task management endpoints."""
import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database import get_db
from src.models.task import Task, TaskStatus
from src.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from src.services.broadcaster import broadcast_task_update

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    project_id: Optional[str] = Query(None),
    status: Optional[TaskStatus] = Query(None),
    limit: int = Query(100, le=500),
    db: AsyncSession = Depends(get_db)
):
    """List tasks with optional filtering."""
    query = select(Task)

    if project_id:
        query = query.where(Task.project_id == project_id)
    if status:
        query = query.where(Task.status == status)

    query = query.limit(limit).order_by(Task.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific task by ID."""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("", response_model=TaskResponse)
async def create_task(task_data: TaskCreate, db: AsyncSession = Depends(get_db)):
    """Create a new task."""
    task = Task(
        id=str(uuid.uuid4()),
        **task_data.model_dump()
    )
    db.add(task)
    await db.flush()
    await broadcast_task_update(task)
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a task."""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_data.model_dump(exclude_unset=True)

    # Track status transitions
    if "status" in update_data:
        new_status = update_data["status"]
        if new_status == TaskStatus.IN_PROGRESS and not task.started_at:
            task.started_at = datetime.utcnow()
        elif new_status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            task.completed_at = datetime.utcnow()

    for field, value in update_data.items():
        setattr(task, field, value)

    await db.flush()
    await broadcast_task_update(task)
    return task


@router.post("/{task_id}/assign/{agent_id}", response_model=TaskResponse)
async def assign_task(
    task_id: str,
    agent_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Assign a task to an agent."""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.assigned_agent_id = agent_id
    task.status = TaskStatus.QUEUED
    await db.flush()
    await broadcast_task_update(task)
    return task
