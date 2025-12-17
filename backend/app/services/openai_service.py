"""OpenAI service for LLM interactions with function calling."""

import logging
from typing import List, Dict, Any, Optional, AsyncIterator
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionChunk
from app.config import settings
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for interacting with OpenAI API with function calling support."""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
    )
    async def create_chat_completion(
        self,
        messages: List[ChatCompletionMessageParam],
        tools: Optional[List[Dict[str, Any]]] = None,
        stream: bool = False,
    ) -> Any:
        """
        Create a chat completion with optional function calling.

        Args:
            messages: List of chat messages
            tools: Optional list of tools/functions available to the model
            stream: Whether to stream the response

        Returns:
            Chat completion response or async iterator for streaming
        """
        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "stream": stream,
            }

            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

            response = await self.client.chat.completions.create(**kwargs)

            return response

        except Exception as e:
            logger.error(f"Error creating chat completion: {e}")
            raise

    async def create_streaming_completion(
        self,
        messages: List[ChatCompletionMessageParam],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> AsyncIterator[ChatCompletionChunk]:
        """
        Create a streaming chat completion.

        Args:
            messages: List of chat messages
            tools: Optional list of tools/functions

        Yields:
            ChatCompletionChunk objects
        """
        stream = await self.create_chat_completion(
            messages=messages,
            tools=tools,
            stream=True,
        )

        async for chunk in stream:
            yield chunk

    async def get_completion_text(
        self,
        messages: List[ChatCompletionMessageParam],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """
        Get completion text (non-streaming).

        Args:
            messages: List of chat messages
            tools: Optional list of tools/functions

        Returns:
            Completion text
        """
        response = await self.create_chat_completion(
            messages=messages,
            tools=tools,
            stream=False,
        )

        return response.choices[0].message.content or ""


# Global instance
openai_service = OpenAIService()
