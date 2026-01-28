"""Audit logging service.

"Audit Everything" - Every agent action must be logged.
"""
import uuid
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.audit import AuditLog, AuditAction
from src.services.broadcaster import broadcast_audit_event


async def log_audit_event(
    db: AsyncSession,
    action: AuditAction,
    description: str,
    agent_id: Optional[str] = None,
    agent_role: Optional[str] = None,
    project_id: Optional[str] = None,
    task_id: Optional[str] = None,
    runplan_id: Optional[str] = None,
    extra_data: Optional[Dict[str, Any]] = None,
    file_path: Optional[str] = None,
    command: Optional[str] = None,
    success: bool = True,
    error_message: Optional[str] = None,
) -> AuditLog:
    """Log an audit event and broadcast to connected clients."""
    audit_log = AuditLog(
        id=str(uuid.uuid4()),
        action=action,
        description=description,
        agent_id=agent_id,
        agent_role=agent_role,
        project_id=project_id,
        task_id=task_id,
        runplan_id=runplan_id,
        extra_data=extra_data,
        file_path=file_path,
        command=command,
        success=success,
        error_message=error_message,
    )
    db.add(audit_log)
    await db.flush()
    await broadcast_audit_event(audit_log)
    return audit_log
