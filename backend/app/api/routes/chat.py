"""Chat API endpoints."""
import logging
import time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.message import ChatRequest, ChatResponse
from app.services.conversation_service import conversation_service
from app.services.agent_service import agent_service
from app.models import MessageRole
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/send", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Send a message and get AI response with tool execution.

    This endpoint implements the React Agent pattern:
    1. User sends a message
    2. Agent reasons about which tools to use
    3. Agent executes tools (stock prices, financial data, etc.)
    4. Agent synthesizes final response

    Args:
        request: Chat request with message and optional conversation_id
        db: Database session

    Returns:
        Chat response with user message and AI response
    """
    try:
        # Create or get conversation
        if request.conversation_id:
            conversation = await conversation_service.get_conversation(
                db, request.conversation_id
            )
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
        else:
            # Auto-generate title from first message (truncated)
            title = request.message[:50] + "..." if len(request.message) > 50 else request.message
            conversation = await conversation_service.create_conversation(
                db, title=title
            )

        # Add user message to conversation
        user_message = await conversation_service.add_message(
            db=db,
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content=request.message,
        )

        # Build conversation history for agent
        messages = await conversation_service.get_messages(db, conversation.id)
        message_history = [
            {
                "role": msg.role.value,
                "content": msg.content,
            }
            for msg in messages
        ]

        # Add system message with financial context
        system_message = {
            "role": "system",
            "content": (
                "You are FinAgent, a financial analyst assistant powered by AI. "
                "You have access to financial tools to help analyze stocks, calculate ratios, "
                "and provide investment insights. Use the available tools to gather data and "
                "provide accurate, well-reasoned financial advice.\n\n"
                "FORMATTING INSTRUCTIONS:\n"
                "- Format ALL responses using proper markdown syntax\n"
                "- Use **bold** for important metrics, numbers, and key findings\n"
                "- Use headers (##, ###) to organize information into sections\n"
                "- Use bullet points (-) or numbered lists for multiple items\n"
                "- Use code blocks with ```language for any code, formulas, or structured data\n"
                "- Use tables (| Header |) when presenting comparative data or multiple metrics\n"
                "- Use > blockquotes for important warnings or disclaimers\n"
                "- Keep responses well-structured, scannable, and professional\n\n"
                "Example format:\n"
                "## Stock Analysis: AAPL\n\n"
                "**Current Price**: $175.50\n"
                "**P/E Ratio**: 28.5\n\n"
                "### Key Metrics\n"
                "- Revenue Growth: 12%\n"
                "- Profit Margin: 25.3%\n\n"
                "> Disclaimer: This is not financial advice."
            ),
        }
        message_history.insert(0, system_message)

        # Execute agent
        start_time = time.time()
        agent_result = await agent_service.execute_agent(
            messages=message_history,
            db=db,
            message_id=user_message.id,  # For tool execution logging
        )
        response_time_ms = int((time.time() - start_time) * 1000)

        # Add assistant message to conversation
        assistant_message = await conversation_service.add_message(
            db=db,
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=agent_result["content"],
            response_time_ms=response_time_ms,
            model_name=settings.openai_model,
        )

        # Commit transaction
        await db.commit()

        # Refresh to get relationships (eagerly load tool_executions)
        await conversation_service.refresh_with_relations(db, user_message)
        await conversation_service.refresh_with_relations(db, assistant_message)

        return ChatResponse(
            conversation_id=conversation.id,
            user_message=user_message,
            assistant_message=assistant_message,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in send_message: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
