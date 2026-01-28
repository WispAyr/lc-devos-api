"""Pydantic schemas for Project."""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


class ProjectBase(BaseModel):
    """Base project schema."""
    name: str
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    """Schema for creating a project."""
    github_repo_url: Optional[str] = None
    github_repo_name: Optional[str] = None
    daily_token_budget: Optional[int] = None
    max_concurrent_runs: int = 3
    config: Optional[Dict[str, Any]] = None


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""
    name: Optional[str] = None
    description: Optional[str] = None
    github_repo_url: Optional[str] = None
    github_repo_name: Optional[str] = None
    daily_token_budget: Optional[int] = None
    max_concurrent_runs: Optional[int] = None
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class ProjectResponse(ProjectBase):
    """Schema for project response."""
    id: str
    github_repo_url: Optional[str]
    github_repo_name: Optional[str]
    daily_token_budget: Optional[int]
    max_concurrent_runs: int
    config: Optional[Dict[str, Any]]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
