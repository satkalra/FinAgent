"""Pydantic schemas for conversations."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ConversationCreate(BaseModel):
    """Schema for creating a conversation."""

    title: str = Field(default="New Conversation", max_length=255)
    user_id: Optional[str] = None


class ConversationUpdate(BaseModel):
    """Schema for updating a conversation."""

    title: Optional[str] = Field(None, max_length=255)


class ConversationResponse(BaseModel):
    """Schema for conversation response."""

    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    user_id: Optional[str]
    model_name: str
    total_messages: int
    total_tokens: int

    class Config:
        from_attributes = True
