"""SSE (Server-Sent Events) manager for streaming responses."""

import json
import logging
from typing import AsyncIterator, Dict, Any

logger = logging.getLogger(__name__)


class SSEManager:
    """Manager for Server-Sent Events streaming."""

    @staticmethod
    def format_sse(data: Dict[str, Any], event: str = "message") -> str:
        """
        Format data as SSE message.

        Args:
            data: Data to send
            event: Event type

        Returns:
            Formatted SSE message
        """
        return f"event: {event}\ndata: {json.dumps(data)}\n\n"

    @staticmethod
    async def stream_events(
        events: AsyncIterator[Dict[str, Any]],
    ) -> AsyncIterator[str]:
        """
        Stream events as SSE.

        Args:
            events: Async iterator of event dictionaries

        Yields:
            Formatted SSE messages
        """
        try:
            async for event in events:
                event_type = event.get("type", "message")
                yield SSEManager.format_sse(event, event=event_type)

        except Exception as e:
            logger.error(f"Error in SSE stream: {e}")
            error_event = {
                "type": "error",
                "error": str(e),
            }
            yield SSEManager.format_sse(error_event, event="error")


# Global instance
sse_manager = SSEManager()
