"""Audit log model - tracks all agent actions for visibility."""
import enum
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, DateTime, Enum, Text, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from src.database import Base


class AuditAction(str, enum.Enum):
    """Types of auditable actions."""
    # Agent lifecycle
    AGENT_STARTED = "AGENT_STARTED"
    AGENT_STOPPED = "AGENT_STOPPED"
    AGENT_STATUS_CHANGE = "AGENT_STATUS_CHANGE"

    # Task operations
    TASK_CREATED = "TASK_CREATED"
    TASK_ASSIGNED = "TASK_ASSIGNED"
    TASK_STARTED = "TASK_STARTED"
    TASK_COMPLETED = "TASK_COMPLETED"
    TASK_FAILED = "TASK_FAILED"

    # RunPlan operations
    RUNPLAN_CREATED = "RUNPLAN_CREATED"
    RUNPLAN_STARTED = "RUNPLAN_STARTED"
    RUNPLAN_STEP_COMPLETED = "RUNPLAN_STEP_COMPLETED"
    RUNPLAN_COMPLETED = "RUNPLAN_COMPLETED"
    RUNPLAN_FAILED = "RUNPLAN_FAILED"

    # Code operations
    FILE_READ = "FILE_READ"
    FILE_WRITE = "FILE_WRITE"
    FILE_DELETE = "FILE_DELETE"
    COMMAND_RUN = "COMMAND_RUN"

    # Decisions
    DECISION_MADE = "DECISION_MADE"
    USER_INPUT_REQUESTED = "USER_INPUT_REQUESTED"
    USER_INPUT_RECEIVED = "USER_INPUT_RECEIVED"

    # Errors
    ERROR_OCCURRED = "ERROR_OCCURRED"

    # Opinions
    OPINION_LOGGED = "OPINION_LOGGED"


class AuditLog(Base):
    """Audit log entry - "If an agent acts, it's logged here"."""
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    # What happened
    action: Mapped[AuditAction] = mapped_column(Enum(AuditAction), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Who did it
    agent_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    agent_role: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Context
    project_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    task_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    runplan_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    # Details
    extra_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # For file/command operations
    file_path: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    command: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Result
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
