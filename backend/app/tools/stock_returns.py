"""Stock returns calculator tool for calculating historical investment returns."""

import yfinance as yf
from typing import Dict, Any, Optional
from app.tools.base import BaseTool
import json
from datetime import datetime, timedelta


class StockReturnsTool(BaseTool):
    """Tool to calculate historical stock investment returns."""

    name = "calculate_stock_returns"
    description = "Calculate what a historical stock investment would be worth today, including total returns and annualized returns"
    display_name = "Stock Returns Calculator"

    async def execute(
        self,
        ticker: str,
        investment_amount: float,
        years_ago: Optional[float] = None,
        start_date: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Calculate historical investment returns for a stock.

        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
            investment_amount: Initial investment amount in dollars
            years_ago: Number of years ago the investment was made (e.g., 3 for 3 years ago)
            start_date: Specific start date in YYYY-MM-DD format (alternative to years_ago)

        Returns:
            JSON string with investment return calculations
        """
        try:
            ticker = ticker.upper()
            stock = yf.Ticker(ticker)

            # Determine the start date
            if years_ago is not None:
                start_dt = datetime.now() - timedelta(days=int(years_ago * 365.25))
                start_date_str = start_dt.strftime("%Y-%m-%d")
            elif start_date is not None:
                start_date_str = start_date
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            else:
                return json.dumps({
                    "ticker": ticker,
                    "success": False,
                    "error": "Must provide either 'years_ago' or 'start_date'",
                })

            # Calculate period for yfinance
            end_dt = datetime.now()
            days_diff = (end_dt - start_dt).days

            # Determine appropriate period string
            if days_diff <= 7:
                period = "5d"
            elif days_diff <= 30:
                period = "1mo"
            elif days_diff <= 90:
                period = "3mo"
            elif days_diff <= 180:
                period = "6mo"
            elif days_diff <= 365:
                period = "1y"
            elif days_diff <= 730:
                period = "2y"
            elif days_diff <= 1825:
                period = "5y"
            else:
                period = "max"

            # Get historical data
            hist = stock.history(period=period)

            if hist.empty:
                return json.dumps({
                    "ticker": ticker,
                    "success": False,
                    "error": f"No historical data available for {ticker}",
                })

            # Get start price (first available price in the period)
            start_price = hist["Close"].iloc[0]
            actual_start_date = hist.index[0].strftime("%Y-%m-%d")

            # Get current price (most recent)
            current_price = hist["Close"].iloc[-1]
            actual_end_date = hist.index[-1].strftime("%Y-%m-%d")

            # Calculate shares purchased
            shares_purchased = investment_amount / start_price

            # Calculate current value
            current_value = shares_purchased * current_price

            # Calculate returns
            total_return_dollars = current_value - investment_amount
            total_return_percent = ((current_value - investment_amount) / investment_amount) * 100

            # Calculate annualized return
            actual_years = (datetime.strptime(actual_end_date, "%Y-%m-%d") -
                          datetime.strptime(actual_start_date, "%Y-%m-%d")).days / 365.25

            if actual_years > 0:
                annualized_return = (((current_value / investment_amount) ** (1 / actual_years)) - 1) * 100
            else:
                annualized_return = total_return_percent

            # Get company info
            stock_info = stock.info
            company_name = stock_info.get("longName") or stock_info.get("shortName") or ticker

            result = {
                "ticker": ticker,
                "company_name": company_name,
                "success": True,
                "investment": {
                    "initial_amount": round(investment_amount, 2),
                    "start_date": actual_start_date,
                    "end_date": actual_end_date,
                    "years_held": round(actual_years, 2),
                },
                "prices": {
                    "start_price": round(start_price, 2),
                    "current_price": round(current_price, 2),
                    "price_change": round(current_price - start_price, 2),
                    "price_change_percent": round(((current_price - start_price) / start_price) * 100, 2),
                },
                "returns": {
                    "shares_purchased": round(shares_purchased, 4),
                    "current_value": round(current_value, 2),
                    "total_return_dollars": round(total_return_dollars, 2),
                    "total_return_percent": round(total_return_percent, 2),
                    "annualized_return_percent": round(annualized_return, 2),
                },
                "note": "Returns calculated using split-adjusted closing prices. Does not include dividends or transaction fees."
            }

            return json.dumps(result, indent=2)

        except Exception as e:
            error_result = {
                "ticker": ticker.upper() if ticker else "UNKNOWN",
                "success": False,
                "error": str(e),
                "message": f"Failed to calculate stock returns: {str(e)}",
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
                "investment_amount": {
                    "type": "number",
                    "description": "Initial investment amount in dollars (e.g., 10000 for $10,000)",
                },
                "years_ago": {
                    "type": "number",
                    "description": "Number of years ago the investment was made (e.g., 3 for 3 years ago, 0.5 for 6 months ago)",
                },
                "start_date": {
                    "type": "string",
                    "description": "Specific start date in YYYY-MM-DD format (alternative to years_ago)",
                },
            },
            "required": ["ticker", "investment_amount"],
        }


# Create instance
stock_returns_tool = StockReturnsTool()
