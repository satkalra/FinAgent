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
    - Extended thinking (GPT-4 reasoning process)
    - Tool execution updates
    - AI response chunks

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

            # Send user message event
            yield sse_manager.format_sse(
                {
                    "type": "user_message",
                    "message_id": user_message.id,
                    "content": message,
                },
                event="user_message"
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

            async for event in agent_service.execute_agent_streaming(
                messages=message_history,
                db=db,
                message_id=user_message.id,
            ):
                # Forward events to client
                if event["type"] == "content_chunk":
                    response_content_chunks.append(event["content"])

                yield sse_manager.format_sse(event, event=event["type"])

            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)

            # Save assistant message
            response_content = "".join(response_content_chunks)
            assistant_message = await conversation_service.add_message(
                db=db,
                conversation_id=conversation.id,
                role=MessageRole.ASSISTANT,
                content=response_content,
                response_time_ms=response_time_ms,
                model_name=settings.openai_model,
            )

            await db.commit()

            # Send completion event
            yield sse_manager.format_sse(
                {
                    "type": "complete",
                    "message_id": assistant_message.id,
                    "response_time_ms": response_time_ms,
                },
                event="complete"
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
