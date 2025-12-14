"""Calculator tool for financial calculations."""
from typing import Dict, Any
from app.tools.base import BaseTool
import json


class CalculatorTool(BaseTool):
    """Tool for performing financial calculations."""

    name = "calculate_investment_returns"
    description = "Calculate investment returns, compound interest, and future value of investments given principal, rate, and time period"

    async def execute(
        self,
        principal: float,
        annual_rate: float,
        years: float,
        monthly_contribution: float = 0.0,
        **kwargs
    ) -> str:
        """
        Calculate investment returns.

        Args:
            principal: Initial investment amount
            annual_rate: Annual interest rate as a percentage (e.g., 7 for 7%)
            years: Number of years to invest
            monthly_contribution: Monthly contribution amount (default: 0)

        Returns:
            JSON string with calculation results
        """
        try:
            rate_decimal = annual_rate / 100
            monthly_rate = rate_decimal / 12
            months = years * 12

            # Calculate future value with compound interest
            if monthly_contribution > 0:
                # Future value of principal
                fv_principal = principal * ((1 + rate_decimal) ** years)

                # Future value of monthly contributions (annuity)
                if monthly_rate > 0:
                    fv_contributions = monthly_contribution * (
                        ((1 + monthly_rate) ** months - 1) / monthly_rate
                    )
                else:
                    fv_contributions = monthly_contribution * months

                future_value = fv_principal + fv_contributions
                total_contributions = principal + (monthly_contribution * months)
            else:
                future_value = principal * ((1 + rate_decimal) ** years)
                total_contributions = principal

            total_returns = future_value - total_contributions
            roi_percent = (total_returns / total_contributions) * 100

            result = {
                "success": True,
                "inputs": {
                    "principal": principal,
                    "annual_rate_percent": annual_rate,
                    "years": years,
                    "monthly_contribution": monthly_contribution,
                },
                "results": {
                    "future_value": round(future_value, 2),
                    "total_contributions": round(total_contributions, 2),
                    "total_returns": round(total_returns, 2),
                    "roi_percent": round(roi_percent, 2),
                },
                "breakdown": {
                    "initial_investment": principal,
                    "total_monthly_contributions": round(monthly_contribution * months, 2),
                    "interest_earned": round(future_value - total_contributions, 2),
                },
            }

            return json.dumps(result, indent=2)

        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "message": "Failed to calculate investment returns",
            }
            return json.dumps(error_result, indent=2)

    def get_schema(self) -> Dict[str, Any]:
        """Get OpenAI function calling schema."""
        return {
            "type": "object",
            "properties": {
                "principal": {
                    "type": "number",
                    "description": "Initial investment amount in dollars",
                },
                "annual_rate": {
                    "type": "number",
                    "description": "Annual interest rate as a percentage (e.g., 7 for 7% annual return)",
                },
                "years": {
                    "type": "number",
                    "description": "Number of years to invest",
                },
                "monthly_contribution": {
                    "type": "number",
                    "description": "Monthly contribution amount in dollars (optional, default: 0)",
                    "default": 0.0,
                },
            },
            "required": ["principal", "annual_rate", "years"],
        }


# Create instance
calculator_tool = CalculatorTool()
