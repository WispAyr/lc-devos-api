"""RunPlan model - execution plans for tasks."""
import enum
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, DateTime, Enum, Text, ForeignKey, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column
from src.database import Base


class RunPlanStatus(str, enum.Enum):
    """RunPlan execution status."""
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class RunPlan(Base):
    """RunPlan - structured execution plan for a task."""
    __tablename__ = "runplans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    task_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tasks.id"), nullable=False
    )

    # Plan details
    skill_name: Mapped[str] = mapped_column(String(100), nullable=False)
    skill_version: Mapped[str] = mapped_column(String(20), default="v1")

    # Input/Output
    inputs: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    outputs: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Execution state
    status: Mapped[RunPlanStatus] = mapped_column(
        Enum(RunPlanStatus),
        default=RunPlanStatus.DRAFT,
        nullable=False
    )
    current_step: Mapped[int] = mapped_column(Integer, default=0)
    total_steps: Mapped[int] = mapped_column(Integer, default=0)

    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)

    # Cost tracking
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)

    # GitHub PR link
    github_pr_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
