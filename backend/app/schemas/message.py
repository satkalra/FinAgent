"""Pydantic schemas for agent status and updates."""

from pydantic import BaseModel
from typing import Optional
from enum import Enum


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
