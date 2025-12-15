"""Agent service implementing React (Reason + Act) pattern."""
import logging
import json
import time
from typing import List, Dict, Any, Optional, AsyncIterator
from openai.types.chat import ChatCompletionMessageParam
from app.services.openai_service import openai_service
from app.tools import tool_registry
from app.database import AsyncSession
from app.models import ToolExecution, Message
from app.schemas.message import AgentStatus, StatusUpdate

logger = logging.getLogger(__name__)


class AgentService:
    """Service implementing React Agent pattern with tool execution."""

    def __init__(self):
        self.openai_service = openai_service
        self.tool_registry = tool_registry
        self.max_iterations = 10  # Prevent infinite loops

    async def execute_agent(
        self,
        messages: List[ChatCompletionMessageParam],
        db: Optional[AsyncSession] = None,
        message_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Execute agent with React loop: Reason → Act → Observe.

        Args:
            messages: Conversation history
            db: Database session for logging tool executions
            message_id: Message ID for associating tool executions

        Returns:
            Dict with final response, tool execution logs, and status updates
        """
        tool_executions = []
        status_updates = []
        iteration = 0

        # Get available tools
        tools = self.tool_registry.get_openai_functions()

        # Initial status
        status_updates.append(StatusUpdate(
            status=AgentStatus.THINKING,
            message="Analyzing your request..."
        ))

        while iteration < self.max_iterations:
            iteration += 1
            logger.info(f"Agent iteration {iteration}")

            # Update status - generating response
            status_updates.append(StatusUpdate(
                status=AgentStatus.GENERATING_RESPONSE,
                message=f"Processing (iteration {iteration})...",
                progress=min(int((iteration / self.max_iterations) * 100), 90)
            ))

            # Call OpenAI with function calling
            response = await self.openai_service.create_chat_completion(
                messages=messages,
                tools=tools if tools else None,
                stream=False,
            )

            assistant_message = response.choices[0].message

            # Check if the model wants to call a function
            if assistant_message.tool_calls:
                # Add assistant message with tool calls to conversation
                messages.append({
                    "role": "assistant",
                    "content": assistant_message.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            }
                        }
                        for tc in assistant_message.tool_calls
                    ]
                })

                # Execute each tool call
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    logger.info(f"Calling tool: {function_name} with args: {function_args}")

                    # Update status - calling tool
                    status_updates.append(StatusUpdate(
                        status=AgentStatus.CALLING_TOOL,
                        message=f"Using {function_name}...",
                        tool_name=function_name
                    ))

                    # Execute tool
                    start_time = time.time()
                    tool_result = await self._execute_tool(
                        function_name,
                        function_args,
                        db=db,
                        message_id=message_id,
                    )
                    execution_time = int((time.time() - start_time) * 1000)

                    # Track execution
                    tool_executions.append({
                        "tool_name": function_name,
                        "tool_input": function_args,
                        "tool_output": tool_result,
                        "execution_time_ms": execution_time,
                    })

                    # Update status - processing results
                    status_updates.append(StatusUpdate(
                        status=AgentStatus.PROCESSING_RESULTS,
                        message=f"Processing results from {function_name}...",
                        tool_name=function_name
                    ))

                    # Add tool result to conversation
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result,
                    })

            else:
                # No more tool calls, return final response
                status_updates.append(StatusUpdate(
                    status=AgentStatus.COMPLETED,
                    message="Response complete",
                    progress=100
                ))
                return {
                    "content": assistant_message.content or "",
                    "tool_executions": tool_executions,
                    "status_updates": status_updates,
                    "iterations": iteration,
                }

        # Max iterations reached
        logger.warning(f"Agent reached max iterations ({self.max_iterations})")
        status_updates.append(StatusUpdate(
            status=AgentStatus.ERROR,
            message="Maximum iterations reached"
        ))
        return {
            "content": "I apologize, but I've reached the maximum number of tool executions. Please try rephrasing your question.",
            "tool_executions": tool_executions,
            "status_updates": status_updates,
            "iterations": iteration,
        }

    async def execute_agent_streaming(
        self,
        messages: List[ChatCompletionMessageParam],
        db: Optional[AsyncSession] = None,
        message_id: Optional[int] = None,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Execute agent with streaming responses.

        Yields:
            Dict with events: thinking, tool_call, tool_result, response, status
        """
        iteration = 0
        tools = self.tool_registry.get_openai_functions()

        # Emit initial status
        yield {
            "type": "status",
            "status": "thinking",
            "message": "Analyzing your request..."
        }

        while iteration < self.max_iterations:
            iteration += 1

            # Emit status update
            yield {
                "type": "status",
                "status": "generating_response",
                "message": f"Processing (iteration {iteration})...",
                "progress": min(int((iteration / self.max_iterations) * 100), 90)
            }

            # Stream the response
            stream = self.openai_service.create_streaming_completion(
                messages=messages,
                tools=tools if tools else None,
            )

            # Collect tool calls and content
            content_chunks = []
            tool_calls_data = []
            current_tool_call = None

            async for chunk in stream:
                delta = chunk.choices[0].delta if chunk.choices else None

                if not delta:
                    continue

                # Handle content (thinking/response)
                if delta.content:
                    content_chunks.append(delta.content)
                    yield {
                        "type": "content_chunk",
                        "content": delta.content,
                    }

                # Handle tool calls
                if delta.tool_calls:
                    for tc_delta in delta.tool_calls:
                        if tc_delta.index is not None:
                            # New tool call or update existing
                            while len(tool_calls_data) <= tc_delta.index:
                                tool_calls_data.append({
                                    "id": "",
                                    "type": "function",
                                    "function": {"name": "", "arguments": ""}
                                })

                            if tc_delta.id:
                                tool_calls_data[tc_delta.index]["id"] = tc_delta.id

                            if tc_delta.function:
                                if tc_delta.function.name:
                                    tool_calls_data[tc_delta.index]["function"]["name"] = tc_delta.function.name
                                if tc_delta.function.arguments:
                                    tool_calls_data[tc_delta.index]["function"]["arguments"] += tc_delta.function.arguments

            # Process tool calls if any
            if tool_calls_data:
                # Add assistant message to conversation
                messages.append({
                    "role": "assistant",
                    "content": "".join(content_chunks) or None,
                    "tool_calls": tool_calls_data,
                })

                # Execute tools
                for tool_call_data in tool_calls_data:
                    function_name = tool_call_data["function"]["name"]
                    function_args = json.loads(tool_call_data["function"]["arguments"])

                    # Emit status - calling tool
                    yield {
                        "type": "status",
                        "status": "calling_tool",
                        "message": f"Using {function_name}...",
                        "tool_name": function_name
                    }

                    # Emit tool call event
                    yield {
                        "type": "tool_call",
                        "tool_name": function_name,
                        "tool_input": function_args,
                    }

                    # Execute tool
                    start_time = time.time()
                    tool_result = await self._execute_tool(
                        function_name,
                        function_args,
                        db=db,
                        message_id=message_id,
                    )
                    execution_time = int((time.time() - start_time) * 1000)

                    # Emit status - processing results
                    yield {
                        "type": "status",
                        "status": "processing_results",
                        "message": f"Processing results from {function_name}...",
                        "tool_name": function_name
                    }

                    # Emit tool result event
                    yield {
                        "type": "tool_result",
                        "tool_name": function_name,
                        "tool_output": tool_result,
                        "execution_time_ms": execution_time,
                    }

                    # Add tool result to conversation
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call_data["id"],
                        "content": tool_result,
                    })
            else:
                # No tool calls, final response
                yield {
                    "type": "status",
                    "status": "completed",
                    "message": "Response complete",
                    "progress": 100
                }
                yield {
                    "type": "final_response",
                    "content": "".join(content_chunks),
                    "iterations": iteration,
                }
                return

        # Max iterations reached
        yield {
            "type": "status",
            "status": "error",
            "message": "Maximum iterations reached"
        }
        yield {
            "type": "error",
            "content": "Maximum iterations reached",
        }

    async def _execute_tool(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        db: Optional[AsyncSession] = None,
        message_id: Optional[int] = None,
    ) -> str:
        """
        Execute a tool and optionally log to database.

        Args:
            tool_name: Name of the tool to execute
            tool_args: Tool arguments
            db: Database session
            message_id: Message ID for logging

        Returns:
            Tool execution result as string
        """
        try:
            tool = self.tool_registry.get_tool(tool_name)
            if not tool:
                error_msg = f"Tool '{tool_name}' not found"
                logger.error(error_msg)
                return json.dumps({"error": error_msg})

            # Execute tool
            result = await tool.execute(**tool_args)

            # Log to database if db session provided
            if db and message_id:
                tool_execution = ToolExecution(
                    message_id=message_id,
                    tool_name=tool_name,
                    tool_input=tool_args,
                    tool_output=result,
                    success=True,
                )
                db.add(tool_execution)
                await db.flush()

            return result

        except Exception as e:
            error_msg = f"Error executing tool '{tool_name}': {str(e)}"
            logger.error(error_msg)

            # Log error to database
            if db and message_id:
                tool_execution = ToolExecution(
                    message_id=message_id,
                    tool_name=tool_name,
                    tool_input=tool_args,
                    tool_output=None,
                    success=False,
                    error_message=str(e),
                )
                db.add(tool_execution)
                await db.flush()

            return json.dumps({"error": error_msg})


# Global instance
agent_service = AgentService()
