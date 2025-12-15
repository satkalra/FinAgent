"""Base tool class for defining agent tools."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ToolParameter(BaseModel):
    """Schema for a tool parameter."""

    type: str
    description: str
    enum: Optional[List[str]] = None
    required: bool = True


class ToolSchema(BaseModel):
    """Schema for a tool definition compatible with OpenAI function calling."""

    name: str
    description: str
    parameters: Dict[str, Any]


class BaseTool(ABC):
    """Abstract base class for agent tools."""

    name: str
    description: str
    display_name: Optional[str] = None

    @abstractmethod
    async def execute(self, **kwargs) -> str:
        """
        Execute the tool with given parameters.

        Args:
            **kwargs: Tool-specific parameters

        Returns:
            str: Tool execution result
        """
        pass

    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """
        Get OpenAI function calling schema for this tool.

        Returns:
            Dict containing the tool schema for OpenAI function calling
        """
        pass

    def to_openai_function(self) -> Dict[str, Any]:
        """
        Convert tool to OpenAI Chat Completions API function format.

        Returns:
            Dict in OpenAI Chat Completions function calling format
        """
        schema = self.get_schema()
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": schema,
            },
        }

    def to_responses_api_tool(self) -> Dict[str, Any]:
        """
        Convert tool to OpenAI Responses API tool format.

        Returns:
            Dict in OpenAI Responses API format
        """
        schema = self.get_schema()
        return {
            "type": "function",
            "name": self.name,
            "description": self.description,
            "parameters": schema,
        }

    def get_display_name(self) -> str:
        """
        Get human-readable tool name for UI/status updates.
        """
        if self.display_name:
            return self.display_name
        return self.name.replace("_", " ").title()


class ToolRegistry:
    """Registry for managing all available tools."""

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        """Register a tool."""
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self._tools.get(name)

    def get_all_tools(self) -> List[BaseTool]:
        """Get all registered tools."""
        return list(self._tools.values())

    def get_openai_functions(self) -> List[Dict[str, Any]]:
        """Get all tools in OpenAI Chat Completions function calling format."""
        return [tool.to_openai_function() for tool in self._tools.values()]

    def get_responses_api_tools(self) -> List[Dict[str, Any]]:
        """Get all tools in OpenAI Responses API format."""
        return [tool.to_responses_api_tool() for tool in self._tools.values()]


# Global tool registry
tool_registry = ToolRegistry()
