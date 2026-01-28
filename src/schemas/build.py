"""Pydantic schemas for Build Phase workflow."""
from pydantic import BaseModel
from typing import Optional


class Requirement(BaseModel):
    """A project requirement."""
    id: str
    type: str  # feature, constraint, user-story
    title: str
    description: str
    priority: str  # must, should, could
    status: str  # draft, confirmed


class TechDecision(BaseModel):
    """A technology stack decision."""
    id: str
    category: str
    choice: str
    reasoning: str
    status: str  # suggested, confirmed


class BuildInitRequest(BaseModel):
    """Request to initialize build phase for a project."""
    project_id: str
    requirements: list[Requirement] = []
    tech_stack: list[TechDecision] = []
    notes: Optional[str] = None
    create_github_repo: bool = False
    github_repo_name: Optional[str] = None


class BuildInitResponse(BaseModel):
    """Response from build initialization."""
    success: bool
    project_id: str
    phase: str  # design, build, deploy
    github_repo_url: Optional[str] = None
    message: str
    next_steps: list[str]
