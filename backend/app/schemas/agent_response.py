"""Pydantic models for agent response schema (for structured outputs)."""

from typing import Any, Optional, Union
from pydantic import BaseModel, Field, ConfigDict


class AgentResponse(BaseModel):
    """Schema for agent's structured JSON response.

    Note: For structured outputs compatibility, action_input is a JSON string
    that will be parsed after receiving the response.
    """

    model_config = ConfigDict(strict=True)

    thought: str = Field(
        ...,
        description="Your rationale for the next step - clear, professional, user-facing reasoning"
    )
    action: str = Field(
        ...,
        description="Tool name to use (e.g., 'get_stock_price', 'calculate_financial_ratios') or 'final_answer'"
    )
    action_input: str = Field(
        ...,
        description="JSON string of parameters for the tool. For tools: stringify the args object. For final_answer: stringify {\"answer\": \"response\"}"
    )
