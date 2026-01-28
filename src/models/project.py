"""Project model - tracks products being built by The Factory."""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, DateTime, Text, JSON, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column
from src.database import Base


class Project(Base):
    """Project (Product) being built by The Factory."""
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Repository info
    github_repo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    github_repo_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Configuration
    config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Cost controls
    daily_token_budget: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_concurrent_runs: Mapped[int] = mapped_column(Integer, default=3)

    # State
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
