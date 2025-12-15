"""Pydantic schemas for messages."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from app.models import MessageRole


class AgentStatus(str, Enum):
    """Enum for agent execution status."""

    IDLE = "idle"
    THINKING = "thinking"
    CALLING_TOOL = "calling_tool"
    PROCESSING_RESULTS = "processing_results"
    GENERATING_RESPONSE = "generating_response"
    COMPLETED = "completed"
    ERROR = "error"


class StatusUpdate(BaseModel):
    """Schema for status updates during agent execution."""

    status: AgentStatus
    message: str
    tool_name: Optional[str] = None
    progress: Optional[int] = None  # 0-100 percentage


class MessageCreate(BaseModel):
    """Schema for creating a message."""

    content: str
    role: MessageRole = MessageRole.USER


class ToolExecutionResponse(BaseModel):
    """Schema for tool execution response."""

    id: int
    tool_name: str
    tool_input: Dict[str, Any]
    tool_output: Optional[str]
    execution_time_ms: Optional[int]
    success: bool
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Schema for message response."""

    id: int
    conversation_id: int
    role: MessageRole
    content: str
    created_at: datetime
    tokens_used: Optional[int]
    response_time_ms: Optional[int]
    model_name: Optional[str]
    tool_executions: List[ToolExecutionResponse] = []

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    """Schema for chat request."""

    message: str = Field(..., min_length=1, max_length=10000)
    conversation_id: Optional[int] = None
    stream: bool = False


class ThoughtStep(BaseModel):
    """Schema for intermediate thinking step."""

    iteration: int
    thought: str
    action: str


class ChatResponse(BaseModel):
    """Schema for chat response."""

    conversation_id: int
    user_message: MessageResponse
    assistant_message: MessageResponse
    status: Optional[AgentStatus] = AgentStatus.COMPLETED
    status_updates: List[StatusUpdate] = []
    thoughts: List[ThoughtStep] = []
