"""Pydantic schemas for RunPlan."""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel
from src.models.runplan import RunPlanStatus


class RunPlanBase(BaseModel):
    """Base runplan schema."""
    skill_name: str
    skill_version: str = "v1"
    inputs: Dict[str, Any]


class RunPlanCreate(RunPlanBase):
    """Schema for creating a runplan."""
    task_id: str


class RunPlanUpdate(BaseModel):
    """Schema for updating a runplan."""
    status: Optional[RunPlanStatus] = None
    current_step: Optional[int] = None
    outputs: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    tokens_used: Optional[int] = None
    github_pr_url: Optional[str] = None


class RunPlanResponse(RunPlanBase):
    """Schema for runplan response."""
    id: str
    task_id: str
    status: RunPlanStatus
    current_step: int
    total_steps: int
    outputs: Optional[Dict[str, Any]]
    error_message: Optional[str]
    retry_count: int
    tokens_used: int
    github_pr_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True
