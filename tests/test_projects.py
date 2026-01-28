import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_project(async_client: AsyncClient):
    """Test creating a new project."""
    payload = {
        "name": "Test Project",
        "description": "A test project description",
        "daily_token_budget": 1000
    }
    response = await async_client.post("/projects", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["description"] == "A test project description"
    assert data["is_active"] is True

@pytest.mark.asyncio
async def test_list_projects(async_client: AsyncClient):
    """Test listing projects."""
    await async_client.post("/projects", json={"name": "List Project"})
    
    response = await async_client.get("/projects")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    names = [p["name"] for p in data]
    assert "List Project" in names
