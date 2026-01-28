"""Pydantic schemas for Design Assistant AI chat."""
from pydantic import BaseModel
from typing import Optional, Literal


class ChatMessage(BaseModel):
    """A single chat message."""
    role: Literal["user", "assistant"]
    content: str


class DesignChatRequest(BaseModel):
    """Request to the Design AI chat endpoint."""
    message: str
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    project_description: Optional[str] = None
    context: Optional[str] = None  # Additional context like current requirements
    history: list[ChatMessage] = []  # Conversation history for multi-turn chat


class DesignChatResponse(BaseModel):
    """Response from the Design AI chat endpoint."""
    message: str
    suggestions: Optional[list[str]] = None


class DesignChatStatus(BaseModel):
    """Status of the Design AI service."""
    status: str
    configured: bool
