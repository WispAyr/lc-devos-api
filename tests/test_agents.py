import pytest
from httpx import AsyncClient
from src.models.agent import AgentRole

@pytest.mark.asyncio
async def test_create_agent(async_client: AsyncClient):
    """Test creating a new agent."""
    payload = {
        "name": "Test Agent",
        "role": AgentRole.GENERAL.value,
        "runner_id": "test-runner-1"
    }
    response = await async_client.post("/agents", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Agent"
    assert data["role"] == AgentRole.GENERAL.value
    assert "id" in data

@pytest.mark.asyncio
async def test_list_agents(async_client: AsyncClient):
    """Test listing agents."""
    # Create one first
    payload = {
        "name": "Listable Agent",
        "role": "GENERAL",
        "runner_id": "test-runner-2"
    }
    await async_client.post("/agents", json=payload)
    
    response = await async_client.get("/agents")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    # Check if our agent is there
    names = [a["name"] for a in data]
    assert "Listable Agent" in names
