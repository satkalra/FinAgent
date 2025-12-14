"""Base tool class for defining agent tools."""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
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
        Convert tool to OpenAI function format.

        Returns:
            Dict in OpenAI function calling format
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
        """Get all tools in OpenAI function calling format."""
        return [tool.to_openai_function() for tool in self._tools.values()]


# Global tool registry
tool_registry = ToolRegistry()
