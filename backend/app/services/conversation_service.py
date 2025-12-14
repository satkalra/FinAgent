"""Conversation service for managing conversations and messages."""
import logging
from typing import List, Optional
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload
from app.database import AsyncSession
from app.models import Conversation, Message, MessageRole

logger = logging.getLogger(__name__)


class ConversationService:
    """Service for conversation and message management."""

    async def create_conversation(
        self,
        db: AsyncSession,
        title: str = "New Conversation",
        user_id: Optional[str] = None,
    ) -> Conversation:
        """Create a new conversation."""
        conversation = Conversation(
            title=title,
            user_id=user_id,
        )
        db.add(conversation)
        await db.flush()
        await db.refresh(conversation)
        return conversation

    async def get_conversation(
        self,
        db: AsyncSession,
        conversation_id: int,
    ) -> Optional[Conversation]:
        """Get a conversation by ID."""
        result = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        return result.scalar_one_or_none()

    async def get_conversations(
        self,
        db: AsyncSession,
        user_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Conversation]:
        """Get all conversations, optionally filtered by user."""
        query = select(Conversation).order_by(desc(Conversation.updated_at))

        if user_id:
            query = query.where(Conversation.user_id == user_id)

        query = query.limit(limit).offset(offset)

        result = await db.execute(query)
        return list(result.scalars().all())

    async def update_conversation(
        self,
        db: AsyncSession,
        conversation_id: int,
        title: Optional[str] = None,
    ) -> Optional[Conversation]:
        """Update a conversation."""
        conversation = await self.get_conversation(db, conversation_id)
        if not conversation:
            return None

        if title:
            conversation.title = title

        await db.flush()
        await db.refresh(conversation)
        return conversation

    async def delete_conversation(
        self,
        db: AsyncSession,
        conversation_id: int,
    ) -> bool:
        """Delete a conversation."""
        conversation = await self.get_conversation(db, conversation_id)
        if not conversation:
            return False

        await db.delete(conversation)
        await db.flush()
        return True

    async def add_message(
        self,
        db: AsyncSession,
        conversation_id: int,
        role: MessageRole,
        content: str,
        tokens_used: Optional[int] = None,
        response_time_ms: Optional[int] = None,
        model_name: Optional[str] = None,
    ) -> Message:
        """Add a message to a conversation."""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tokens_used=tokens_used,
            response_time_ms=response_time_ms,
            model_name=model_name,
        )
        db.add(message)
        await db.flush()

        # Update conversation stats
        conversation = await self.get_conversation(db, conversation_id)
        if conversation:
            conversation.total_messages += 1
            if tokens_used:
                conversation.total_tokens += tokens_used

        await db.refresh(message)
        return message

    async def get_messages(
        self,
        db: AsyncSession,
        conversation_id: int,
        limit: Optional[int] = None,
    ) -> List[Message]:
        """Get messages for a conversation."""
        query = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
            .options(selectinload(Message.tool_executions))
        )

        if limit:
            query = query.limit(limit)

        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_message(
        self,
        db: AsyncSession,
        message_id: int,
    ) -> Optional[Message]:
        """Get a single message by ID."""
        result = await db.execute(
            select(Message)
            .where(Message.id == message_id)
            .options(selectinload(Message.tool_executions))
        )
        return result.scalar_one_or_none()

    async def refresh_with_relations(
        self,
        db: AsyncSession,
        message: Message,
    ) -> Message:
        """Refresh a message and eagerly load its relationships."""
        await db.refresh(message, ["tool_executions"])
        return message


# Global instance
conversation_service = ConversationService()
