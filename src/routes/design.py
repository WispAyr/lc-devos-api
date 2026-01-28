"""Design Assistant routes - DEPRECATED, use /mcp/design instead.

Design chat now routes through the MCP agent ecosystem rather than
making direct Anthropic API calls. This avoids double token burn
since agents (Claude sessions) are already running and can handle
design requests as part of their normal workflow.

See: /mcp/design (POST) - Submit design request
See: /mcp/design/respond (POST) - Agent response endpoint
See: /mcp/design/{request_id} (GET) - Poll for response
"""
import os
from fastapi import APIRouter, HTTPException

from src.schemas.design import DesignChatRequest, DesignChatResponse

router = APIRouter(prefix="/design", tags=["design"])


@router.post("/chat", response_model=DesignChatResponse)
async def design_chat(request: DesignChatRequest) -> DesignChatResponse:
    """DEPRECATED: Use /mcp/design instead.

    Design chat now routes through the MCP agent ecosystem.
    This avoids burning extra tokens since agents are already running.
    """
    raise HTTPException(
        status_code=410,  # Gone
        detail="This endpoint is deprecated. Use POST /mcp/design to route design requests through the agent ecosystem. Responses come via WebSocket (DESIGN_RESPONSE) or polling GET /mcp/design/{request_id}."
    )


@router.get("/health")
async def design_health():
    """Check Design AI service status."""
    return {
        "status": "deprecated",
        "message": "Design chat now routes through MCP agent ecosystem",
        "use_instead": "/mcp/design",
        "documentation": "POST /mcp/design submits request, response via WebSocket DESIGN_RESPONSE or GET /mcp/design/{request_id}",
    }
