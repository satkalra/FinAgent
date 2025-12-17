"""Financial tools for FinAgent."""

from app.tools.base import tool_registry
from app.tools.stock_price import stock_price_tool
from app.tools.company_info import company_info_tool
from app.tools.financial_ratios import financial_ratios_tool
from app.tools.calculator import calculator_tool

# Register all tools
tool_registry.register(stock_price_tool)
tool_registry.register(company_info_tool)
tool_registry.register(financial_ratios_tool)
tool_registry.register(calculator_tool)

__all__ = [
    "tool_registry",
    "stock_price_tool",
    "company_info_tool",
    "financial_ratios_tool",
    "calculator_tool",
]
