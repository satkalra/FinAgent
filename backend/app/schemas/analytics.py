"""Pydantic schemas for analytics."""
from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class AnalyticsOverview(BaseModel):
    """Schema for analytics overview."""

    total_conversations: int
    total_messages: int
    total_evaluations: int
    average_rating: Optional[float]
    average_quality_score: Optional[float]
    total_tokens_used: int
    average_response_time_ms: Optional[float]
    most_used_model: Optional[str]
    tool_executions: int
    most_used_tool: Optional[str]


class ToolUsageStats(BaseModel):
    """Schema for tool usage statistics."""

    tool_name: str
    execution_count: int
    success_count: int
    failure_count: int
    average_execution_time_ms: Optional[float]


class QualityMetrics(BaseModel):
    """Schema for quality metrics."""

    average_rating: Optional[float]
    average_quality_score: Optional[float]
    average_accuracy_score: Optional[float]
    average_relevance_score: Optional[float]
    average_helpfulness_score: Optional[float]
    average_tool_usage_quality: Optional[float]
    total_evaluations: int
