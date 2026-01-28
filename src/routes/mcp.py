"""MCP (Model Context Protocol) agent-to-agent messaging endpoints."""
import json
import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException
from src.websocket.manager import connection_manager
from src.schemas.mcp import (
    AgentMessageRequest,
    BroadcastMessageRequest,
    AgentRegisterRequest,
    MCPAgentInfo,
    MCPAgentResponse,
    MessageSentResponse,
    DesignRequestPayload,
    DesignRequestSubmission,
    DesignResponsePayload,
    PendingDesignRequest,
)

router = APIRouter(prefix="/mcp", tags=["MCP"])

# In-memory store for registered MCP agents
# In production, this would be stored in the database
_registered_agents: dict[str, MCPAgentInfo] = {}

# In-memory store for pending design requests
# Key: request_id, Value: PendingDesignRequest
_pending_design_requests: dict[str, PendingDesignRequest] = {}


async def broadcast_agent_message(
    message_id: str,
    source_agent: str,
    target_agent: Optional[str],
    message: str,
    priority: str,
    message_type: str,
) -> None:
    """Broadcast an agent message via WebSocket."""
    payload = {
        "type": "AGENT_MESSAGE",
        "payload": {
            "message_id": message_id,
            "source_agent": source_agent,
            "target_agent": target_agent,
            "message": message,
            "priority": priority,
            "message_type": message_type,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }
    await connection_manager.broadcast(json.dumps(payload))


@router.post("/message", response_model=MessageSentResponse)
async def send_message(request: AgentMessageRequest):
    """Send a message to a specific agent.

    The message is broadcast via WebSocket with type "AGENT_MESSAGE".
    Target agent must be registered to receive the message.
    """
    # Verify target agent is registered
    if request.target_agent not in _registered_agents:
        raise HTTPException(
            status_code=404,
            detail=f"Target agent '{request.target_agent}' is not registered"
        )

    message_id = str(uuid.uuid4())

    # Broadcast via WebSocket
    await broadcast_agent_message(
        message_id=message_id,
        source_agent="api",  # Could be enhanced to track source
        target_agent=request.target_agent,
        message=request.message,
        priority=request.priority.value,
        message_type=request.type.value,
    )

    # Update last_seen for target agent
    _registered_agents[request.target_agent].last_seen = datetime.utcnow()

    return MessageSentResponse(
        success=True,
        message_id=message_id,
        delivered_to=request.target_agent,
        timestamp=datetime.utcnow(),
    )


@router.post("/broadcast", response_model=MessageSentResponse)
async def broadcast_message(request: BroadcastMessageRequest):
    """Broadcast a message to all registered agents.

    The message is sent to all connected WebSocket clients.
    """
    if not _registered_agents:
        raise HTTPException(
            status_code=400,
            detail="No agents registered to receive broadcast"
        )

    message_id = str(uuid.uuid4())
    agent_ids = list(_registered_agents.keys())

    # Broadcast via WebSocket to all
    await broadcast_agent_message(
        message_id=message_id,
        source_agent="api",
        target_agent=None,  # Broadcast to all
        message=request.message,
        priority=request.priority.value,
        message_type="notification",
    )

    return MessageSentResponse(
        success=True,
        message_id=message_id,
        delivered_to=agent_ids,
        timestamp=datetime.utcnow(),
    )


@router.get("/agents", response_model=list[MCPAgentInfo])
async def list_agents():
    """List all registered MCP agents and their status."""
    return list(_registered_agents.values())


@router.post("/register", response_model=MCPAgentResponse)
async def register_agent(request: AgentRegisterRequest):
    """Register an agent with the MCP system.

    Agents must be registered before they can send or receive messages.
    Re-registering an existing agent updates its capabilities.
    """
    is_update = request.agent_id in _registered_agents

    _registered_agents[request.agent_id] = MCPAgentInfo(
        agent_id=request.agent_id,
        capabilities=request.capabilities,
        status="online",
        registered_at=datetime.utcnow() if not is_update else _registered_agents[request.agent_id].registered_at,
        last_seen=datetime.utcnow(),
    )

    return MCPAgentResponse(
        agent_id=request.agent_id,
        registered=True,
        message="Agent updated successfully" if is_update else "Agent registered successfully",
    )


@router.delete("/agents/{agent_id}", response_model=MCPAgentResponse)
async def unregister_agent(agent_id: str):
    """Unregister an agent from the MCP system."""
    if agent_id not in _registered_agents:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{agent_id}' is not registered"
        )

    del _registered_agents[agent_id]

    return MCPAgentResponse(
        agent_id=agent_id,
        registered=False,
        message="Agent unregistered successfully",
    )


# ============================================================================
# Design Chat via MCP - Routes design requests through agent ecosystem
# ============================================================================

@router.post("/design", response_model=DesignRequestSubmission)
async def submit_design_request(payload: DesignRequestPayload):
    """Submit a design assistance request to be handled by an agent.

    The request is broadcast via WebSocket with type "DESIGN_REQUEST".
    Agents listening can pick up the request and respond via /mcp/design/respond.
    Frontend should listen on WebSocket for "DESIGN_RESPONSE" with matching request_id.
    """
    request_id = str(uuid.uuid4())

    # Store the pending request
    pending = PendingDesignRequest(
        request_id=request_id,
        payload=payload,
        submitted_at=datetime.utcnow(),
        status="pending",
    )
    _pending_design_requests[request_id] = pending

    # Broadcast the design request via WebSocket
    ws_payload = {
        "type": "DESIGN_REQUEST",
        "payload": {
            "request_id": request_id,
            "message": payload.message,
            "project_id": payload.project_id,
            "project_name": payload.project_name,
            "project_description": payload.project_description,
            "context": payload.context,
            "history": [{"role": m.role, "content": m.content} for m in payload.history],
        },
        "timestamp": datetime.utcnow().isoformat(),
    }
    await connection_manager.broadcast(json.dumps(ws_payload))

    return DesignRequestSubmission(
        request_id=request_id,
        status="pending",
        message="Design request submitted. Listen on WebSocket for DESIGN_RESPONSE.",
    )


@router.post("/design/respond")
async def respond_to_design_request(response: DesignResponsePayload):
    """Agent endpoint to respond to a pending design request.

    The response is broadcast via WebSocket with type "DESIGN_RESPONSE".
    Frontend receives this and displays the AI response.
    """
    if response.request_id not in _pending_design_requests:
        raise HTTPException(
            status_code=404,
            detail=f"Design request '{response.request_id}' not found or already completed"
        )

    pending = _pending_design_requests[response.request_id]

    # Update the pending request
    pending.status = "completed"
    pending.response = response.response
    pending.responded_by = response.agent_id

    # Broadcast the response via WebSocket
    ws_payload = {
        "type": "DESIGN_RESPONSE",
        "payload": {
            "request_id": response.request_id,
            "agent_id": response.agent_id,
            "response": response.response,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }
    await connection_manager.broadcast(json.dumps(ws_payload))

    # Clean up completed request (keep for a bit for polling fallback)
    # In production, would use TTL or scheduled cleanup

    return {
        "success": True,
        "request_id": response.request_id,
        "message": "Response delivered",
    }


@router.get("/design/{request_id}")
async def get_design_request_status(request_id: str):
    """Get the status of a design request (polling fallback).

    Use this if WebSocket is not available.
    """
    if request_id not in _pending_design_requests:
        raise HTTPException(
            status_code=404,
            detail=f"Design request '{request_id}' not found"
        )

    pending = _pending_design_requests[request_id]
    return {
        "request_id": pending.request_id,
        "status": pending.status,
        "response": pending.response,
        "responded_by": pending.responded_by,
        "submitted_at": pending.submitted_at.isoformat(),
    }


@router.get("/design")
async def list_pending_design_requests():
    """List all pending design requests waiting for agent response.

    Agents can use this to see what requests need handling.
    """
    pending = [
        {
            "request_id": req.request_id,
            "message": req.payload.message,
            "project_name": req.payload.project_name,
            "status": req.status,
            "submitted_at": req.submitted_at.isoformat(),
        }
        for req in _pending_design_requests.values()
        if req.status == "pending"
    ]
    return {"pending_requests": pending, "count": len(pending)}
