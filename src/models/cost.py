"""Cost tracking model - BeanCounter data."""
from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, DateTime, Date, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from src.database import Base


class CostRecord(Base):
    """Cost tracking record - tracks token usage and costs."""
    __tablename__ = "cost_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    # What incurred the cost
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id"), nullable=False
    )
    agent_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    runplan_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    # Token counts
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)

    # Cost calculation (in USD cents)
    estimated_cost_cents: Mapped[int] = mapped_column(Integer, default=0)

    # Date for daily aggregation
    record_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
