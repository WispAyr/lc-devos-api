"""Pydantic schemas for MCP (Model Context Protocol) agent messaging."""
from datetime import datetime
from enum import Enum
from typing import Optional, Union
from pydantic import BaseModel


class MessagePriority(str, Enum):
    """Priority levels for agent messages."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class MessageType(str, Enum):
    """Types of agent messages."""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    COMMAND = "command"


class AgentMessageRequest(BaseModel):
    """Schema for sending a message to a specific agent."""
    target_agent: str
    message: str
    priority: MessagePriority = MessagePriority.NORMAL
    type: MessageType = MessageType.NOTIFICATION


class BroadcastMessageRequest(BaseModel):
    """Schema for broadcasting a message to all agents."""
    message: str
    priority: MessagePriority = MessagePriority.NORMAL


class AgentRegisterRequest(BaseModel):
    """Schema for registering an agent with MCP."""
    agent_id: str
    capabilities: list[str] = []


class MCPAgentInfo(BaseModel):
    """Information about a registered MCP agent."""
    agent_id: str
    capabilities: list[str]
    status: str
    registered_at: datetime
    last_seen: Optional[datetime] = None


class MCPAgentResponse(BaseModel):
    """Response schema for agent registration."""
    agent_id: str
    registered: bool
    message: str


class MessageSentResponse(BaseModel):
    """Response schema for message sending operations."""
    success: bool
    message_id: str
    delivered_to: Union[str, list[str]]
    timestamp: datetime


# Design Chat via MCP
class DesignChatMessage(BaseModel):
    """A single message in a design chat conversation."""
    role: str  # 'user' or 'assistant'
    content: str


class DesignRequestPayload(BaseModel):
    """Payload for a design assistance request routed through MCP."""
    message: str
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    project_description: Optional[str] = None
    context: Optional[str] = None
    history: list[DesignChatMessage] = []


class DesignRequestSubmission(BaseModel):
    """Response when a design request is submitted to the queue."""
    request_id: str
    status: str  # 'pending', 'processing', 'completed', 'timeout'
    message: str


class DesignResponsePayload(BaseModel):
    """Payload for an agent responding to a design request."""
    request_id: str
    agent_id: str
    response: str


class PendingDesignRequest(BaseModel):
    """Internal model for tracking pending design requests."""
    request_id: str
    payload: DesignRequestPayload
    submitted_at: datetime
    status: str = "pending"
    response: Optional[str] = None
    responded_by: Optional[str] = None
