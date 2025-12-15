"""Company information tool for getting company details."""
import yfinance as yf
from typing import Dict, Any
from app.tools.base import BaseTool
import json


class CompanyInfoTool(BaseTool):
    """Tool to get detailed company information."""

    name = "get_company_info"
    description = "Get detailed company information including sector, industry, employees, description, and key executives for a given ticker symbol"
    display_name = "Company Insights"

    async def execute(self, ticker: str, **kwargs) -> str:
        """
        Get company information.

        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT')

        Returns:
            JSON string with company information
        """
        try:
            stock = yf.Ticker(ticker.upper())
            info = stock.info

            result = {
                "ticker": ticker.upper(),
                "success": True,
                "company_name": info.get("longName") or info.get("shortName"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "website": info.get("website"),
                "description": info.get("longBusinessSummary"),
                "employees": info.get("fullTimeEmployees"),
                "headquarters": {
                    "city": info.get("city"),
                    "state": info.get("state"),
                    "country": info.get("country"),
                },
                "market_info": {
                    "market_cap": info.get("marketCap"),
                    "enterprise_value": info.get("enterpriseValue"),
                    "currency": info.get("currency", "USD"),
                },
                "key_executives": [],
            }

            # Get key executives
            if "companyOfficers" in info and info["companyOfficers"]:
                for officer in info["companyOfficers"][:5]:  # Top 5 executives
                    result["key_executives"].append({
                        "name": officer.get("name"),
                        "title": officer.get("title"),
                        "age": officer.get("age"),
                    })

            return json.dumps(result, indent=2)

        except Exception as e:
            error_result = {
                "ticker": ticker.upper(),
                "success": False,
                "error": str(e),
                "message": f"Failed to get company info for {ticker.upper()}",
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
company_info_tool = CompanyInfoTool()
