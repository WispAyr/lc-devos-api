"""Local Connect DevOS API - The Coordinator.

"Radical Visibility" - If an agent acts, the Frontend MUST know.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from src.config import get_settings
from src.database import init_db
from src.websocket.manager import connection_manager
from src.routes import (
    agents_router,
    tasks_router,
    projects_router,
    runplans_router,
    audit_router,
    costs_router,
    health_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown."""
    # Startup
    await init_db()
    yield
    # Shutdown
    pass


app = FastAPI(
    title="Local Connect DevOS API",
    description="The Factory Coordinator - Manages agent state and broadcasts visibility",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS configuration for frontend
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)
app.include_router(agents_router)
app.include_router(tasks_router)
app.include_router(projects_router)
app.include_router(runplans_router)
app.include_router(audit_router)
app.include_router(costs_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "lc-devos-api",
        "status": "operational",
        "version": "0.1.0",
        "websocket": "/ws",
        "docs": "/docs"
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates.

    Connect to receive:
    - AGENT_UPDATE: Agent status changes
    - TASK_UPDATE: Task state changes
    - RUNPLAN_UPDATE: RunPlan execution updates
    - AUDIT_EVENT: All logged agent actions
    """
    await connection_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, handle incoming messages if needed
            data = await websocket.receive_text()
            # Echo back for ping/pong or handle commands
            if data == "ping":
                await connection_manager.send_personal_message("pong", websocket)
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)


@app.get("/ws/status")
async def websocket_status():
    """Get WebSocket connection status."""
    return {
        "active_connections": connection_manager.connection_count,
        "endpoint": "/ws"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.api_port, reload=True)
