"""Agent model - tracks AI agent instances and their state."""
import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Enum, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column
from src.database import Base


class AgentStatus(str, enum.Enum):
    """Agent status states as defined in architecture."""
    IDLE = "IDLE"
    PLANNING = "PLANNING"
    EXECUTING = "EXECUTING"
    VERIFYING = "VERIFYING"
    AWAITING_INPUT = "AWAITING_INPUT"
    OFFLINE = "OFFLINE"


class AgentRole(str, enum.Enum):
    """Specialized agent roles."""
    ARCHITECT = "ARCHITECT"
    FRONTEND_BOT = "FRONTEND_BOT"
    BACKEND_BOT = "BACKEND_BOT"
    RELEASE_BOT = "RELEASE_BOT"
    BEAN_COUNTER = "BEAN_COUNTER"
    GENERAL = "GENERAL"


class Agent(Base):
    """Agent instance tracking."""
    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[AgentRole] = mapped_column(
        Enum(AgentRole),
        default=AgentRole.GENERAL,
        nullable=False
    )
    status: Mapped[AgentStatus] = mapped_column(
        Enum(AgentStatus),
        default=AgentStatus.IDLE,
        nullable=False
    )
    current_task: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    current_action: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    runner_id: Mapped[str] = mapped_column(String(50), nullable=False)

    # Cost tracking
    tokens_used_today: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens_used: Mapped[int] = mapped_column(Integer, default=0)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    last_heartbeat: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
