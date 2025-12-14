"""Pydantic schemas for evaluations."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class EvaluationCreate(BaseModel):
    """Schema for creating an evaluation."""

    message_id: int
    conversation_id: int
    rating: int = Field(..., ge=1, le=5)
    quality_score: Optional[float] = Field(None, ge=0, le=100)
    accuracy_score: Optional[float] = Field(None, ge=0, le=100)
    relevance_score: Optional[float] = Field(None, ge=0, le=100)
    helpfulness_score: Optional[float] = Field(None, ge=0, le=100)
    tool_usage_quality: Optional[float] = Field(None, ge=0, le=100)
    feedback_text: Optional[str] = None
    evaluator_notes: Optional[str] = None


class EvaluationUpdate(BaseModel):
    """Schema for updating an evaluation."""

    rating: Optional[int] = Field(None, ge=1, le=5)
    quality_score: Optional[float] = Field(None, ge=0, le=100)
    accuracy_score: Optional[float] = Field(None, ge=0, le=100)
    relevance_score: Optional[float] = Field(None, ge=0, le=100)
    helpfulness_score: Optional[float] = Field(None, ge=0, le=100)
    tool_usage_quality: Optional[float] = Field(None, ge=0, le=100)
    feedback_text: Optional[str] = None
    evaluator_notes: Optional[str] = None


class EvaluationResponse(BaseModel):
    """Schema for evaluation response."""

    id: int
    message_id: int
    conversation_id: int
    rating: int
    quality_score: Optional[float]
    accuracy_score: Optional[float]
    relevance_score: Optional[float]
    helpfulness_score: Optional[float]
    tool_usage_quality: Optional[float]
    feedback_text: Optional[str]
    evaluator_notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
