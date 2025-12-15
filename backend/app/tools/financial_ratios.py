"""Financial ratios tool for calculating key financial metrics."""
import yfinance as yf
from typing import Dict, Any
from app.tools.base import BaseTool
import json


class FinancialRatiosTool(BaseTool):
    """Tool to get financial ratios and metrics."""

    name = "calculate_financial_ratios"
    description = "Calculate and get key financial ratios including P/E, PEG, P/B, ROE, ROA, profit margins, debt ratios, and dividend yield"
    display_name = "Financial Ratios"

    async def execute(self, ticker: str, **kwargs) -> str:
        """
        Get financial ratios and metrics.

        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT')

        Returns:
            JSON string with financial ratios
        """
        try:
            stock = yf.Ticker(ticker.upper())
            info = stock.info

            result = {
                "ticker": ticker.upper(),
                "success": True,
                "company_name": info.get("longName") or info.get("shortName"),
                "valuation_ratios": {
                    "pe_ratio": info.get("trailingPE"),
                    "forward_pe": info.get("forwardPE"),
                    "peg_ratio": info.get("pegRatio"),
                    "price_to_book": info.get("priceToBook"),
                    "price_to_sales": info.get("priceToSalesTrailing12Months"),
                    "enterprise_to_revenue": info.get("enterpriseToRevenue"),
                    "enterprise_to_ebitda": info.get("enterpriseToEbitda"),
                },
                "profitability_ratios": {
                    "profit_margin": info.get("profitMargins"),
                    "operating_margin": info.get("operatingMargins"),
                    "gross_margin": info.get("grossMargins"),
                    "roe": info.get("returnOnEquity"),
                    "roa": info.get("returnOnAssets"),
                },
                "financial_health": {
                    "current_ratio": info.get("currentRatio"),
                    "quick_ratio": info.get("quickRatio"),
                    "debt_to_equity": info.get("debtToEquity"),
                    "total_debt": info.get("totalDebt"),
                    "total_cash": info.get("totalCash"),
                },
                "dividend_info": {
                    "dividend_yield": info.get("dividendYield"),
                    "payout_ratio": info.get("payoutRatio"),
                    "dividend_rate": info.get("dividendRate"),
                },
                "growth_metrics": {
                    "earnings_growth": info.get("earningsGrowth"),
                    "revenue_growth": info.get("revenueGrowth"),
                    "earnings_quarterly_growth": info.get("earningsQuarterlyGrowth"),
                },
            }

            # Convert None values to null and format percentages
            result = json.loads(json.dumps(result))

            return json.dumps(result, indent=2)

        except Exception as e:
            error_result = {
                "ticker": ticker.upper(),
                "success": False,
                "error": str(e),
                "message": f"Failed to calculate financial ratios for {ticker.upper()}",
            }
            return json.dumps(error_result, indent=2)

    def get_schema(self) -> Dict[str, Any]:
        """Get OpenAI function calling schema."""
        return {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol (e.g., 'AAPL' for Apple, 'MSFT' for Microsoft)",
                },
            },
            "required": ["ticker"],
        }


# Create instance
financial_ratios_tool = FinancialRatiosTool()
