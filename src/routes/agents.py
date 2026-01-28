"""Agent management endpoints."""
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database import get_db
from src.models.agent import Agent, AgentStatus
from src.schemas.agent import AgentCreate, AgentUpdate, AgentResponse, AgentStatusUpdate
from src.services.broadcaster import broadcast_agent_update

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("", response_model=list[AgentResponse])
async def list_agents(db: AsyncSession = Depends(get_db)):
    """List all agents."""
    result = await db.execute(select(Agent))
    return result.scalars().all()


@router.get("/active", response_model=list[AgentResponse])
async def list_active_agents(db: AsyncSession = Depends(get_db)):
    """List only active (non-offline) agents."""
    result = await db.execute(
        select(Agent).where(Agent.status != AgentStatus.OFFLINE)
    )
    return result.scalars().all()


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific agent by ID."""
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.post("", response_model=AgentResponse)
async def create_agent(agent_data: AgentCreate, db: AsyncSession = Depends(get_db)):
    """Register a new agent."""
    agent = Agent(
        id=str(uuid.uuid4()),
        **agent_data.model_dump()
    )
    db.add(agent)
    await db.flush()
    await broadcast_agent_update(agent)
    return agent


@router.patch("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    agent_data: AgentUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an agent."""
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    for field, value in agent_data.model_dump(exclude_unset=True).items():
        setattr(agent, field, value)

    await db.flush()
    await broadcast_agent_update(agent)
    return agent


@router.patch("/{agent_id}/status", response_model=AgentResponse)
async def update_agent_status(
    agent_id: str,
    status_data: AgentStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update agent status - broadcasts to all connected clients."""
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent.status = status_data.status
    if status_data.current_action is not None:
        agent.current_action = status_data.current_action

    await db.flush()
    await broadcast_agent_update(agent)
    return agent


@router.post("/{agent_id}/heartbeat", response_model=AgentResponse)
async def agent_heartbeat(agent_id: str, db: AsyncSession = Depends(get_db)):
    """Update agent heartbeat timestamp."""
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent.last_heartbeat = datetime.utcnow()
    await db.flush()
    return agent
