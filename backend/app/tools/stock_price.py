"""Stock price tool for getting stock prices using yfinance."""
import yfinance as yf
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from app.tools.base import BaseTool
import json


class StockPriceTool(BaseTool):
    """Tool to get stock prices and basic information."""

    name = "get_stock_price"
    description = "Get current stock price, historical prices, and basic stock information for a given ticker symbol"
    display_name = "Stock Price Lookup"

    async def execute(
        self,
        ticker: str,
        period: str = "1d",
        info: bool = True,
        **kwargs
    ) -> str:
        """
        Get stock price information.

        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
            period: Time period for historical data ('1d', '5d', '1mo', '3mo', '1y')
            info: Whether to include basic stock information

        Returns:
            JSON string with stock price data
        """
        try:
            stock = yf.Ticker(ticker.upper())

            result = {
                "ticker": ticker.upper(),
                "success": True,
            }

            # Get current price and basic info
            if info:
                stock_info = stock.info
                result["current_price"] = stock_info.get("currentPrice") or stock_info.get("regularMarketPrice")
                result["currency"] = stock_info.get("currency", "USD")
                result["company_name"] = stock_info.get("longName") or stock_info.get("shortName")
                result["market_cap"] = stock_info.get("marketCap")
                result["previous_close"] = stock_info.get("previousClose")
                result["open"] = stock_info.get("open")
                result["day_high"] = stock_info.get("dayHigh")
                result["day_low"] = stock_info.get("dayLow")
                result["volume"] = stock_info.get("volume")

                # Calculate price change
                if result.get("current_price") and result.get("previous_close"):
                    change = result["current_price"] - result["previous_close"]
                    change_percent = (change / result["previous_close"]) * 100
                    result["change"] = round(change, 2)
                    result["change_percent"] = round(change_percent, 2)

            # Get historical data if requested
            if period != "1d":
                hist = stock.history(period=period)
                if not hist.empty:
                    result["historical_data"] = {
                        "period": period,
                        "start_date": hist.index[0].strftime("%Y-%m-%d"),
                        "end_date": hist.index[-1].strftime("%Y-%m-%d"),
                        "high": round(hist["High"].max(), 2),
                        "low": round(hist["Low"].min(), 2),
                        "average": round(hist["Close"].mean(), 2),
                    }

            return json.dumps(result, indent=2)

        except Exception as e:
            error_result = {
                "ticker": ticker.upper(),
                "success": False,
                "error": str(e),
                "message": f"Failed to get stock price for {ticker.upper()}",
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
                "period": {
                    "type": "string",
                    "description": "Time period for historical data",
                    "enum": ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y"],
                    "default": "1d",
                },
                "info": {
                    "type": "boolean",
                    "description": "Whether to include detailed stock information",
                    "default": True,
                },
            },
            "required": ["ticker"],
        }


# Create instance
stock_price_tool = StockPriceTool()
