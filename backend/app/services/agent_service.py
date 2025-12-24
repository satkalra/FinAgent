"""Agent service implementing React (Reason + Act) pattern with intermediate thinking."""

import json
import logging
import re
import time
from typing import Any, AsyncIterator, Dict, List, Optional
from app.schemas.message import AgentStatus, StatusUpdate
from app.schemas.agent_response import AgentResponse
from app.services.openai_service import openai_service
from app.tools import tool_registry
from openai.types.chat import ChatCompletionMessageParam

logger = logging.getLogger(__name__)


class AgentService:
    """Service implementing React Agent pattern with tool execution and intermediate thinking."""

    def __init__(self):
        self.openai_service = openai_service
        self.tool_registry = tool_registry
        self.max_iterations = 10  # Prevent infinite loops

    def _extract_json_from_response(self, content: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from model response, handling markdown code blocks."""
        if not content:
            return None

        # Try to parse as direct JSON first
        try:
            return json.loads(content.strip())
        except json.JSONDecodeError:
            pass

        # Try to extract JSON from markdown code block
        json_pattern = r"```(?:json)?\s*(\{.*?\})\s*```"
        matches = re.findall(json_pattern, content, re.DOTALL)
        if matches:
            try:
                return json.loads(matches[0])
            except json.JSONDecodeError:
                pass

        # Try to find JSON object without code block
        json_obj_pattern = r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}"
        matches = re.findall(json_obj_pattern, content, re.DOTALL)
        for match in matches:
            try:
                obj = json.loads(match)
                if "thought" in obj and "action" in obj:
                    return obj
            except json.JSONDecodeError:
                continue

        return None

    def _get_tool_display_name(self, tool_name: str) -> str:
        """Return a human-readable tool name for UI/status updates."""
        tool = self.tool_registry.get_tool(tool_name)
        if tool:
            try:
                return tool.get_display_name()
            except AttributeError:
                pass
        return tool_name.replace("_", " ").title()

    async def execute_agent(
        self,
        messages: List[ChatCompletionMessageParam],
    ) -> Dict[str, Any]:
        """
        Execute agent with React loop using structured JSON responses.

        Args:
            messages: Conversation history
            db: Database session for logging tool executions
            message_id: Message ID for associating tool executions

        Returns:
            Dict with final response, tool execution logs, status updates, and thoughts
        """
        tool_executions = []
        status_updates = []
        thoughts = []  # Track all intermediate thoughts
        iteration = 0

        # Initial status
        status_updates.append(
            StatusUpdate(
                status=AgentStatus.THINKING, message="Analyzing your request..."
            )
        )

        while iteration < self.max_iterations:
            iteration += 1
            logger.info(f"Agent iteration {iteration}")

            # Update status - generating response
            status_updates.append(
                StatusUpdate(
                    status=AgentStatus.GENERATING_RESPONSE,
                    message=f"Reasoning (step {iteration})...",
                    progress=min(int((iteration / self.max_iterations) * 100), 90),
                )
            )

            # Call OpenAI with structured outputs for guaranteed JSON
            response = await self.openai_service.create_chat_completion(
                messages=messages,
                tools=None,
                stream=False,
                response_format=AgentResponse,
            )

            # With parse(), the structured object is in .parsed attribute
            parsed_obj: AgentResponse = response.choices[0].message.parsed
            assistant_content = response.choices[0].message.content or ""

            if parsed_obj:
                # Direct access to Pydantic model fields
                thought = parsed_obj.thought
                action = parsed_obj.action
                # Parse action_input from JSON string to dict
                try:
                    action_input = json.loads(parsed_obj.action_input)
                except json.JSONDecodeError:
                    logger.warning("Failed to parse action_input: %s", parsed_obj.action_input)
                    action_input = {}
            else:
                # Fallback if parsing failed (should never happen)
                logger.error("Structured output parsing returned None")
                status_updates.append(
                    StatusUpdate(
                        status=AgentStatus.COMPLETED,
                        message="Response complete",
                        progress=100,
                    )
                )
                return {
                    "content": assistant_content,
                    "tool_executions": tool_executions,
                    "status_updates": status_updates,
                    "thoughts": thoughts,
                    "iterations": iteration,
                }
            display_action = action
            if action and action != "final_answer":
                display_action = self._get_tool_display_name(action)

            # Track the thought
            if thought:
                thoughts.append(
                    {
                        "iteration": iteration,
                        "thought": thought,
                        "action": display_action,
                    }
                )
                logger.info(f"Thought: {thought}")

            # Add assistant message to conversation
            messages.append(
                {
                    "role": "assistant",
                    "content": assistant_content,
                }
            )

            # Check if final answer
            if action == "final_answer":
                final_answer = action_input.get("answer", "")
                status_updates.append(
                    StatusUpdate(
                        status=AgentStatus.COMPLETED,
                        message="Response complete",
                        progress=100,
                    )
                )
                return {
                    "content": final_answer,
                    "tool_executions": tool_executions,
                    "status_updates": status_updates,
                    "thoughts": thoughts,
                    "iterations": iteration,
                }

            # Execute tool if action is a tool name
            if action and action != "final_answer":
                tool_display_name = display_action or action
                # Update status - calling tool
                status_updates.append(
                    StatusUpdate(
                        status=AgentStatus.CALLING_TOOL,
                        message=f"Using {tool_display_name}...",
                        tool_name=tool_display_name,
                    )
                )

                logger.info(f"Calling tool: {action} with args: {action_input}")

                # Execute tool
                start_time = time.time()
                tool_result = await self._execute_tool(
                    action,
                    action_input,
                )
                execution_time = int((time.time() - start_time) * 1000)

                # Track execution
                tool_executions.append(
                    {
                        "tool_name": tool_display_name,
                        "tool_input": action_input,
                        "tool_output": tool_result,
                        "execution_time_ms": execution_time,
                    }
                )

                # Update status - processing results
                status_updates.append(
                    StatusUpdate(
                        status=AgentStatus.PROCESSING_RESULTS,
                        message=f"Processing results from {tool_display_name}...",
                        tool_name=tool_display_name,
                    )
                )

                # Add tool result as user message (observation)
                messages.append(
                    {
                        "role": "user",
                        "content": f"Tool result from {tool_display_name}:\n{tool_result}",
                    }
                )

        # Max iterations reached
        logger.warning(f"Agent reached max iterations ({self.max_iterations})")
        status_updates.append(
            StatusUpdate(status=AgentStatus.ERROR, message="Maximum iterations reached")
        )
        return {
            "content": "I apologize, but I've reached the maximum number of reasoning steps. Please try rephrasing your question or breaking it into smaller parts.",
            "tool_executions": tool_executions,
            "status_updates": status_updates,
            "thoughts": thoughts,
            "iterations": iteration,
        }

    async def execute_agent_streaming(
        self,
        messages: List[ChatCompletionMessageParam],
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Execute agent with streaming responses and intermediate thinking.

        Yields:
            Dict with events: thought, tool_call, tool_result, final_answer, status
        """
        iteration = 0

        # Emit initial status
        yield {
            "type": "status",
            "status": "thinking",
            "message": "Analyzing your request...",
        }

        while iteration < self.max_iterations:
            iteration += 1

            # Emit status update
            yield {
                "type": "status",
                "status": "generating_response",
                "message": f"Reasoning (step {iteration})...",
                "progress": min(int((iteration / self.max_iterations) * 100), 90),
            }

            # Use structured outputs for guaranteed JSON response
            response = await self.openai_service.create_chat_completion(
                messages=messages,
                tools=None,
                stream=False,
                response_format=AgentResponse,
            )

            # With parse(), the structured object is in .parsed attribute
            parsed_obj = response.choices[0].message.parsed
            full_content = response.choices[0].message.content or ""

            if parsed_obj:
                # Direct access to Pydantic model fields
                thought = parsed_obj.thought
                action = parsed_obj.action
                # Parse action_input from JSON string to dict
                try:
                    action_input = json.loads(parsed_obj.action_input)
                except json.JSONDecodeError:
                    logger.warning("Failed to parse action_input: %s", parsed_obj.action_input)
                    action_input = {}
            else:
                # Fallback if parsing failed (should never happen)
                logger.error("Structured output parsing returned None")
                yield {
                    "type": "final_answer",
                    "content": full_content,
                    "iterations": iteration,
                }
                return
            display_action = action
            if action and action != "final_answer":
                display_action = self._get_tool_display_name(action)

            # Emit thought with status update
            if thought:
                # Send status event with the thought content
                yield {"type": "status", "status": "thinking", "message": thought}

                # Also emit thought event for detailed info
                yield {
                    "type": "thought",
                    "iteration": iteration,
                    "thought": thought,
                    "action": display_action,
                }

            # Add assistant message to conversation
            messages.append(
                {
                    "role": "assistant",
                    "content": full_content,
                }
            )

            # Check if final answer
            if action == "final_answer":
                final_answer = action_input.get("answer", "")

                # Stream the final answer word by word for better UX
                words = final_answer.split(' ')
                for i, word in enumerate(words):
                    chunk = word if i == 0 else ' ' + word
                    yield {
                        "type": "content_chunk",
                        "content": chunk,
                    }

                # Signal completion (frontend will create message from accumulated chunks)
                yield {
                    "type": "status",
                    "status": "completed",
                    "message": "Response complete",
                    "progress": 100,
                }
                return

            # Execute tool if action is a tool name
            if action and action != "final_answer":
                tool_display_name = display_action or action
                # Emit status - calling tool
                yield {
                    "type": "status",
                    "status": "calling_tool",
                    "message": f"Using {tool_display_name}...",
                    "tool_name": tool_display_name,
                    "tool_internal_name": action,
                }

                # Emit tool call event
                yield {
                    "type": "tool_call",
                    "tool_name": tool_display_name,
                    "tool_internal_name": action,
                    "tool_input": action_input,
                }

                # Execute tool
                start_time = time.time()
                tool_result = await self._execute_tool(
                    action,
                    action_input,
                )
                execution_time = int((time.time() - start_time) * 1000)

                # Emit status - processing results
                yield {
                    "type": "status",
                    "status": "processing_results",
                    "message": f"Processing results from {tool_display_name}...",
                    "tool_name": tool_display_name,
                    "tool_internal_name": action,
                }

                # Emit tool result event
                yield {
                    "type": "tool_result",
                    "tool_name": tool_display_name,
                    "tool_internal_name": action,
                    "tool_output": tool_result,
                    "execution_time_ms": execution_time,
                }

                # Add tool result as observation
                messages.append(
                    {
                        "role": "user",
                        "content": f"Tool result from {tool_display_name}:\n{tool_result}",
                    }
                )

        # Max iterations reached
        yield {
            "type": "status",
            "status": "error",
            "message": "Maximum iterations reached",
        }
        yield {
            "type": "error",
            "content": "Maximum iterations reached",
        }

    async def _execute_tool(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
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

            return result

        except Exception as e:
            error_msg = f"Error executing tool '{tool_name}': {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})


# Global instance
agent_service = AgentService()
