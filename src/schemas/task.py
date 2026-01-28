"""Pydantic schemas for Task."""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from src.models.task import TaskStatus, TaskPriority


class TaskBase(BaseModel):
    """Base task schema."""
    title: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM


class TaskCreate(TaskBase):
    """Schema for creating a task."""
    project_id: str
    github_issue_url: Optional[str] = None
    monday_item_id: Optional[str] = None
    task_metadata: Optional[Dict[str, Any]] = None


class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assigned_agent_id: Optional[str] = None
    error_message: Optional[str] = None
    task_metadata: Optional[Dict[str, Any]] = None


class TaskResponse(TaskBase):
    """Schema for task response."""
    id: str
    project_id: str
    status: TaskStatus
    assigned_agent_id: Optional[str]
    github_issue_url: Optional[str]
    monday_item_id: Optional[str]
    error_message: Optional[str]
    task_metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True
