"""Tests for MCP (Model Context Protocol) agent messaging endpoints."""
import pytest
from httpx import AsyncClient

# Import the in-memory store to reset between tests
from src.routes.mcp import _registered_agents


@pytest.fixture(autouse=True)
def reset_registered_agents():
    """Clear registered agents before each test."""
    _registered_agents.clear()
    yield
    _registered_agents.clear()


@pytest.mark.asyncio
async def test_register_agent(async_client: AsyncClient):
    """Test registering a new agent."""
    response = await async_client.post(
        "/mcp/register",
        json={
            "agent_id": "test-agent-1",
            "capabilities": ["read", "write", "execute"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["agent_id"] == "test-agent-1"
    assert data["registered"] is True
    assert "registered" in data["message"].lower()


@pytest.mark.asyncio
async def test_register_agent_update(async_client: AsyncClient):
    """Test re-registering an existing agent updates it."""
    # Register first time
    await async_client.post(
        "/mcp/register",
        json={"agent_id": "test-agent-1", "capabilities": ["read"]}
    )

    # Re-register with new capabilities
    response = await async_client.post(
        "/mcp/register",
        json={"agent_id": "test-agent-1", "capabilities": ["read", "write"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["agent_id"] == "test-agent-1"
    assert "updated" in data["message"].lower()


@pytest.mark.asyncio
async def test_list_agents_empty(async_client: AsyncClient):
    """Test listing agents when none are registered."""
    response = await async_client.get("/mcp/agents")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_agents_with_agents(async_client: AsyncClient):
    """Test listing registered agents."""
    # Register two agents
    await async_client.post(
        "/mcp/register",
        json={"agent_id": "agent-1", "capabilities": ["read"]}
    )
    await async_client.post(
        "/mcp/register",
        json={"agent_id": "agent-2", "capabilities": ["write"]}
    )

    response = await async_client.get("/mcp/agents")
    assert response.status_code == 200
    agents = response.json()
    assert len(agents) == 2
    agent_ids = [a["agent_id"] for a in agents]
    assert "agent-1" in agent_ids
    assert "agent-2" in agent_ids


@pytest.mark.asyncio
async def test_unregister_agent(async_client: AsyncClient):
    """Test unregistering an agent."""
    # Register first
    await async_client.post(
        "/mcp/register",
        json={"agent_id": "test-agent", "capabilities": []}
    )

    # Unregister
    response = await async_client.delete("/mcp/agents/test-agent")
    assert response.status_code == 200
    data = response.json()
    assert data["agent_id"] == "test-agent"
    assert data["registered"] is False

    # Verify it's gone
    list_response = await async_client.get("/mcp/agents")
    assert list_response.json() == []


@pytest.mark.asyncio
async def test_unregister_agent_not_found(async_client: AsyncClient):
    """Test unregistering a non-existent agent returns 404."""
    response = await async_client.delete("/mcp/agents/nonexistent")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_send_message_to_registered_agent(async_client: AsyncClient):
    """Test sending a message to a registered agent."""
    # Register target agent
    await async_client.post(
        "/mcp/register",
        json={"agent_id": "target-agent", "capabilities": ["receive"]}
    )

    # Send message
    response = await async_client.post(
        "/mcp/message",
        json={
            "target_agent": "target-agent",
            "message": "Hello from test",
            "priority": "normal",
            "type": "notification"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["delivered_to"] == "target-agent"
    assert "message_id" in data


@pytest.mark.asyncio
async def test_send_message_to_unregistered_agent(async_client: AsyncClient):
    """Test sending a message to an unregistered agent returns 404."""
    response = await async_client.post(
        "/mcp/message",
        json={
            "target_agent": "nonexistent-agent",
            "message": "Hello",
        }
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_broadcast_message(async_client: AsyncClient):
    """Test broadcasting a message to all registered agents."""
    # Register agents
    await async_client.post(
        "/mcp/register",
        json={"agent_id": "agent-1", "capabilities": []}
    )
    await async_client.post(
        "/mcp/register",
        json={"agent_id": "agent-2", "capabilities": []}
    )

    # Broadcast
    response = await async_client.post(
        "/mcp/broadcast",
        json={
            "message": "Broadcast message",
            "priority": "high"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert set(data["delivered_to"]) == {"agent-1", "agent-2"}


@pytest.mark.asyncio
async def test_broadcast_message_no_agents(async_client: AsyncClient):
    """Test broadcasting when no agents are registered returns 400."""
    response = await async_client.post(
        "/mcp/broadcast",
        json={"message": "Hello nobody"}
    )
    assert response.status_code == 400
