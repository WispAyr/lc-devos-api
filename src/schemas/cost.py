"""Pydantic schemas for Cost tracking."""
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel


class CostRecordResponse(BaseModel):
    """Schema for cost record response."""
    id: str
    project_id: str
    agent_id: Optional[str]
    runplan_id: Optional[str]
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost_cents: int
    record_date: date
    created_at: datetime

    class Config:
        from_attributes = True


class CostSummary(BaseModel):
    """Summary of costs for a project."""
    project_id: str
    total_tokens_today: int
    total_tokens_all_time: int
    estimated_cost_today_cents: int
    estimated_cost_all_time_cents: int
    daily_token_budget: Optional[int]
    budget_remaining_today: Optional[int]
    budget_percentage_used: Optional[float]
