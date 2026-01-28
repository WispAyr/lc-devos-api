"""Pydantic schemas for Audit Log."""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel
from src.models.audit import AuditAction


class AuditLogResponse(BaseModel):
    """Schema for audit log response."""
    id: str
    action: AuditAction
    description: str
    agent_id: Optional[str]
    agent_role: Optional[str]
    project_id: Optional[str]
    task_id: Optional[str]
    runplan_id: Optional[str]
    extra_data: Optional[Dict[str, Any]]
    file_path: Optional[str]
    command: Optional[str]
    success: bool
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
