"""SSE (Server-Sent Events) endpoints for real-time streaming."""

import json
import logging
from typing import Any, Dict, List

from app.core.sse_manager import sse_manager
from app.prompts.prompt_utils import render_prompt
from app.services.agent_service import agent_service
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., min_length=1, description="User message")
    history: List[Dict[str, str]] = Field(default_factory=list, description="Chat history")


@router.post("/chat")
async def stream_chat(request: ChatRequest):
    """Stream chat responses over SSE without any persistence layer."""

    async def event_generator():
        """Generate SSE events for the chat stream."""
        try:
            # Sanitize history
            sanitized_history = []
            for item in request.history:
                if not isinstance(item, dict):
                    continue
                content = item.get("content")
                if not content:
                    continue
                sanitized_history.append(
                    {
                        "role": item.get("role", "user"),
                        "content": content,
                    }
                )

            system_message = {
                "role": "system",
                "content": render_prompt("fin_react_agent"),
            }
            message_history = [
                system_message,
                *sanitized_history,
                {"role": "user", "content": request.message},
            ]

            response_content_chunks: List[str] = []
            final_response_text = ""

            async for event in agent_service.execute_agent_streaming(
                messages=message_history,
            ):
                event_type = event.get("type")

                if event_type == "content_chunk":
                    chunk = event.get("content", "")
                    if chunk:
                        response_content_chunks.append(chunk)
                    yield sse_manager.format_sse(
                        {
                            "type": "answer",
                            "chunk": chunk,
                            "is_final": False,
                        },
                        event="answer",
                    )
                elif event_type == "thought":
                    # Emit thought event with detailed thinking steps
                    yield sse_manager.format_sse(
                        {
                            "type": "thought",
                            "iteration": event.get("iteration"),
                            "thought": event.get("thought"),
                            "action": event.get("action"),
                        },
                        event="thought",
                    )
                elif event_type == "status":
                    # Pass through status events from agent
                    yield sse_manager.format_sse(
                        {
                            "type": "status",
                            "status": event.get("status"),
                            "message": event.get("message"),
                            "progress": event.get("progress"),
                            "tool_name": event.get("tool_name"),
                            "tool_internal_name": event.get("tool_internal_name"),
                        },
                        event="status",
                    )
                elif event_type == "tool_call":
                    display_name = event.get("tool_name") or event.get(
                        "tool_internal_name"
                    )
                    yield sse_manager.format_sse(
                        {
                            "type": "status",
                            "status": "tool_call",
                            "message": f"Running tool: {display_name}",
                            "tool_name": display_name,
                            "tool_internal_name": event.get("tool_internal_name"),
                            "tool_input": event.get("tool_input"),
                        },
                        event="status",
                    )
                elif event_type == "tool_result":
                    display_name = event.get("tool_name") or event.get(
                        "tool_internal_name"
                    )
                    yield sse_manager.format_sse(
                        {
                            "type": "status",
                            "status": "tool_result",
                            "message": f"Tool {display_name} completed",
                            "tool_name": display_name,
                            "tool_internal_name": event.get("tool_internal_name"),
                            "tool_output": event.get("tool_output"),
                            "execution_time_ms": event.get("execution_time_ms"),
                        },
                        event="status",
                    )
                elif event_type == "final_answer":
                    final_response_text = event.get("content", "")
                    yield sse_manager.format_sse(
                        {
                            "type": "answer",
                            "content": final_response_text,
                            "is_final": True,
                            "iterations": event.get("iterations"),
                        },
                        event="answer",
                    )
                elif event_type == "error":
                    yield sse_manager.format_sse(
                        {
                            "type": "status",
                            "status": "error",
                            "message": event.get("content")
                            or event.get("error")
                            or "Unknown error",
                        },
                        event="status",
                    )

            # Notify completion
            yield sse_manager.format_sse(
                {
                    "type": "status",
                    "status": "completed",
                    "message": "Streaming complete",
                },
                event="status",
            )

        except Exception as e:  # pylint: disable=broad-except
            logger.error("Error in chat stream: %s", e)
            yield sse_manager.format_sse({"error": str(e)}, event="error")

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )
