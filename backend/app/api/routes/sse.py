"""SSE (Server-Sent Events) endpoints for real-time streaming."""
import logging
import time
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.conversation_service import conversation_service
from app.services.agent_service import agent_service
from app.core.sse_manager import sse_manager
from app.models import MessageRole
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/chat/{conversation_id}")
async def stream_chat(
    conversation_id: int,
    message: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    """
    Stream chat responses with SSE including:
    - Status updates for each stage of processing
    - Tool execution updates
    - Streaming AI response chunks

    Args:
        conversation_id: Conversation ID
        message: User message
        db: Database session

    Returns:
        StreamingResponse with SSE events
    """

    async def event_generator():
        """Generate SSE events for the chat stream."""
        try:
            # Get conversation
            conversation = await conversation_service.get_conversation(db, conversation_id)
            if not conversation:
                yield sse_manager.format_sse(
                    {"error": "Conversation not found"},
                    event="error"
                )
                return

            # Add user message
            user_message = await conversation_service.add_message(
                db=db,
                conversation_id=conversation.id,
                role=MessageRole.USER,
                content=message,
            )

            # Send user message status
            yield sse_manager.format_sse(
                {
                    "type": "status",
                    "status": "user_saved",
                    "message": "User message received",
                    "message_id": user_message.id,
                    "role": MessageRole.USER.value,
                },
                event="status"
            )

            # Build conversation history
            messages = await conversation_service.get_messages(db, conversation.id)
            message_history = [
                {
                    "role": msg.role.value,
                    "content": msg.content,
                }
                for msg in messages
            ]

            # Add system message
            system_message = {
                "role": "system",
                "content": (
                    "You are FinAgent, a financial analyst assistant powered by AI. "
                    "You have access to financial tools to help analyze stocks, calculate ratios, "
                    "and provide investment insights. Use the available tools to gather data and "
                    "provide accurate, well-reasoned financial advice. Be concise and professional."
                ),
            }
            message_history.insert(0, system_message)

            # Stream agent execution
            start_time = time.time()
            response_content_chunks = []
            final_response_text = ""

            async for event in agent_service.execute_agent_streaming(
                messages=message_history,
                db=db,
                message_id=user_message.id,
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
                elif event_type == "tool_call":
                    yield sse_manager.format_sse(
                        {
                            "type": "status",
                            "status": "tool_call",
                            "message": f"Running tool: {event.get('tool_name')}",
                            "tool_name": event.get("tool_name"),
                            "tool_input": event.get("tool_input"),
                        },
                        event="status",
                    )
                elif event_type == "tool_result":
                    yield sse_manager.format_sse(
                        {
                            "type": "status",
                            "status": "tool_result",
                            "message": f"Tool {event.get('tool_name')} completed",
                            "tool_name": event.get("tool_name"),
                            "tool_output": event.get("tool_output"),
                            "execution_time_ms": event.get("execution_time_ms"),
                        },
                        event="status",
                    )
                elif event_type == "final_response":
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
                            "message": event.get("content") or event.get("error") or "Unknown error",
                        },
                        event="status",
                    )

            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)

            # Save assistant message
            response_content = final_response_text or "".join(response_content_chunks)
            assistant_message = await conversation_service.add_message(
                db=db,
                conversation_id=conversation.id,
                role=MessageRole.ASSISTANT,
                content=response_content,
                response_time_ms=response_time_ms,
                model_name=settings.openai_model,
            )

            await db.commit()

            # Send assistant saved status
            yield sse_manager.format_sse(
                {
                    "type": "status",
                    "status": "assistant_saved",
                    "message": "Assistant response saved",
                    "message_id": assistant_message.id,
                    "response_time_ms": response_time_ms,
                    "role": MessageRole.ASSISTANT.value,
                },
                event="status"
            )

            # Notify completion
            yield sse_manager.format_sse(
                {
                    "type": "status",
                    "status": "complete",
                    "message": "Streaming complete",
                    "conversation_id": conversation.id,
                },
                event="status"
            )

        except Exception as e:
            logger.error(f"Error in chat stream: {e}")
            yield sse_manager.format_sse(
                {"error": str(e)},
                event="error"
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )
