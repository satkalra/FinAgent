"""Pydantic schemas for evaluation system."""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal


class TestCase(BaseModel):
    """Schema for a single test case from CSV."""

    test_id: str = Field(..., description="Unique identifier for the test case")
    query: str = Field(..., description="User query to test")
    expected_tool: str = Field(..., description="Expected tool name (internal name)")
    expected_args: Dict[str, Any] = Field(..., description="Expected tool arguments")
    expected_response_contains: str = Field(
        ...,
        description="Keywords/phrases that should appear in response"
    )


class ToolCall(BaseModel):
    """Schema for extracted tool call data."""

    tool_name: str = Field(..., description="Internal tool name")
    tool_display_name: str = Field(..., description="Human-readable tool name")
    arguments: Dict[str, Any] = Field(..., description="Tool arguments")
    output: str = Field(..., description="Tool execution result")
    execution_time_ms: int = Field(..., description="Execution time in milliseconds")


class MetricScore(BaseModel):
    """Schema for a single metric result."""

    metric_name: Literal["tool_selection", "argument_match", "faithfulness"] = Field(
        ...,
        description="Name of the metric"
    )
    score: float = Field(..., ge=0.0, le=1.0, description="Score from 0.0 to 1.0")
    details: Optional[str] = Field(None, description="Additional details or explanation")


class EvaluationResult(BaseModel):
    """Schema for complete evaluation result of one test case."""

    test_id: str = Field(..., description="Test case identifier")
    query: str = Field(..., description="User query that was tested")
    expected_tool: str = Field(..., description="Expected tool name")
    actual_tools: List[str] = Field(..., description="List of tools actually called")
    actual_response: str = Field(..., description="Agent's final response")
    metrics: List[MetricScore] = Field(..., description="Metric scores for this test")
    overall_score: float = Field(..., ge=0.0, le=1.0, description="Average of all metrics")
    passed: bool = Field(..., description="Whether test passed (score >= threshold)")


class EvaluationSummary(BaseModel):
    """Schema for aggregated evaluation metrics across all tests."""

    total_tests: int = Field(..., description="Total number of test cases")
    passed: int = Field(..., description="Number of tests that passed")
    failed: int = Field(..., description="Number of tests that failed")
    average_tool_selection: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Average tool selection accuracy"
    )
    average_argument_match: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Average argument match score"
    )
    average_faithfulness: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Average response faithfulness score"
    )
    overall_average: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Overall average across all metrics"
    )


class TestCaseStartEvent(BaseModel):
    """SSE event when starting a test case."""

    type: Literal["test_case_start"] = "test_case_start"
    test_id: str
    query: str
    current: int = Field(..., description="Current test number (1-indexed)")
    total: int = Field(..., description="Total number of tests")


class StatusEvent(BaseModel):
    """SSE event for status updates."""

    type: Literal["status"] = "status"
    message: str
    progress: Optional[int] = Field(None, ge=0, le=100, description="Progress percentage")


class ErrorEvent(BaseModel):
    """SSE event for errors."""

    type: Literal["error"] = "error"
    test_id: Optional[str] = None
    message: str
    continue_evaluation: bool = Field(
        True,
        alias="continue",
        description="Whether evaluation should continue"
    )
