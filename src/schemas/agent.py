"""Pydantic schemas for Agent."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from src.models.agent import AgentStatus, AgentRole


class AgentBase(BaseModel):
    """Base agent schema."""
    name: str
    role: AgentRole = AgentRole.GENERAL
    runner_id: str


class AgentCreate(AgentBase):
    """Schema for creating an agent."""
    pass


class AgentUpdate(BaseModel):
    """Schema for updating an agent."""
    name: Optional[str] = None
    role: Optional[AgentRole] = None
    current_task: Optional[str] = None
    current_action: Optional[str] = None


class AgentStatusUpdate(BaseModel):
    """Schema for updating agent status."""
    status: AgentStatus
    current_action: Optional[str] = None


class AgentResponse(AgentBase):
    """Schema for agent response."""
    id: str
    status: AgentStatus
    current_task: Optional[str]
    current_action: Optional[str]
    tokens_used_today: int
    total_tokens_used: int
    created_at: datetime
    updated_at: datetime
    last_heartbeat: Optional[datetime]

    class Config:
        from_attributes = True
