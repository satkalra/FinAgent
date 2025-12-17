"""Evaluator classes for computing evaluation metrics."""

import json
import logging
from typing import Dict, Any, List, Tuple
from app.services.openai_service import openai_service
from app.prompts.prompt_utils import render_prompt

logger = logging.getLogger(__name__)


class ToolSelectionEvaluator:
    """
    Evaluates whether the agent selected the correct tool.

    Scoring:
    - 1.0: Expected tool was called
    - 0.0: Expected tool was not called
    """

    def evaluate(self, expected_tool: str, actual_tools: List[str]) -> float:
        """
        Evaluate tool selection accuracy.

        Args:
            expected_tool: Internal name of expected tool
            actual_tools: List of internal names of tools actually called

        Returns:
            1.0 if expected tool in actual_tools, else 0.0
        """
        if expected_tool in actual_tools:
            logger.debug(
                f"Tool selection PASS: expected '{expected_tool}', "
                f"actual {actual_tools}"
            )
            return 1.0
        else:
            logger.debug(
                f"Tool selection FAIL: expected '{expected_tool}', "
                f"actual {actual_tools}"
            )
            return 0.0


class ArgumentMatchEvaluator:
    """
    Evaluates whether tool arguments match expected values.

    Scoring:
    - 1.0: All expected arguments present with matching values
    - 0.0-0.99: Partial match based on percentage of matching fields
    - 0.0: No arguments match
    """

    def evaluate(
        self,
        expected_args: Dict[str, Any],
        actual_args: Dict[str, Any]
    ) -> float:
        """
        Evaluate argument match accuracy.

        Args:
            expected_args: Dictionary of expected arguments
            actual_args: Dictionary of actual arguments from tool call

        Returns:
            Score from 0.0 to 1.0 based on field-level comparison
        """
        if not expected_args:
            # If no expected args, perfect match
            return 1.0

        if not actual_args:
            # If expected args but no actual args, fail
            logger.debug("Argument match FAIL: no actual arguments provided")
            return 0.0

        matching_fields = 0
        total_fields = len(expected_args)

        for key, expected_value in expected_args.items():
            actual_value = actual_args.get(key)

            if actual_value is None:
                logger.debug(f"Argument match: missing field '{key}'")
                continue

            if self._values_match(expected_value, actual_value):
                matching_fields += 1
                logger.debug(
                    f"Argument match: field '{key}' matches "
                    f"(expected={expected_value}, actual={actual_value})"
                )
            else:
                logger.debug(
                    f"Argument match: field '{key}' mismatch "
                    f"(expected={expected_value}, actual={actual_value})"
                )

        score = matching_fields / total_fields
        logger.debug(
            f"Argument match score: {score:.2f} "
            f"({matching_fields}/{total_fields} fields)"
        )
        return score

    def _values_match(self, expected: Any, actual: Any) -> bool:
        """
        Compare two values with normalization.

        Handles:
        - Case-insensitive string comparison
        - Numeric comparison with small epsilon
        - Boolean comparison
        - Nested dict comparison (recursive)
        - List comparison
        """
        # Normalize and compare
        expected_norm = self._normalize_value(expected)
        actual_norm = self._normalize_value(actual)

        if isinstance(expected_norm, dict) and isinstance(actual_norm, dict):
            # Recursive comparison for nested dicts
            return self._dicts_match(expected_norm, actual_norm)

        if isinstance(expected_norm, list) and isinstance(actual_norm, list):
            # List comparison (order matters)
            if len(expected_norm) != len(actual_norm):
                return False
            return all(
                self._values_match(e, a)
                for e, a in zip(expected_norm, actual_norm)
            )

        if isinstance(expected_norm, float) and isinstance(actual_norm, float):
            # Float comparison with epsilon
            return abs(expected_norm - actual_norm) < 1e-6

        return expected_norm == actual_norm

    def _normalize_value(self, value: Any) -> Any:
        """
        Normalize value for comparison.

        - Strings: lowercase
        - Numbers: convert int to float for comparison
        - Others: return as-is
        """
        if isinstance(value, str):
            return value.lower().strip()

        if isinstance(value, int):
            return float(value)

        return value

    def _dicts_match(self, expected: Dict, actual: Dict) -> bool:
        """Check if two dicts match (all expected keys present with matching values)."""
        for key, expected_value in expected.items():
            actual_value = actual.get(key)
            if actual_value is None or not self._values_match(expected_value, actual_value):
                return False
        return True


class ResponseFaithfulnessEvaluator:
    """
    Evaluates whether the agent's response is faithful to tool outputs
    using LLM-as-a-judge.

    Scoring:
    - 0.0-1.0: Score from GPT-4o based on faithfulness criteria
    """

    async def evaluate(
        self,
        query: str,
        expected_contains: str,
        actual_response: str,
        tool_outputs: List[str]
    ) -> Tuple[float, str]:
        """
        Evaluate response faithfulness using LLM judge.

        Args:
            query: Original user query
            expected_contains: Keywords/phrases that should be in response
            actual_response: Agent's final response
            tool_outputs: List of tool output strings

        Returns:
            Tuple of (score: 0.0-1.0, explanation: str)
        """
        try:
            # Render prompt from template
            prompt_content = render_prompt(
                "faithfulness_judge",
                {
                    "query": query,
                    "expected_contains": expected_contains,
                    "actual_response": actual_response,
                    "tool_outputs": tool_outputs
                }
            )

            # Call OpenAI with temperature=0 for deterministic results
            response = await openai_service.create_chat_completion(
                messages=[{"role": "user", "content": prompt_content}],
                temperature=0
            )

            # Parse JSON response
            response_content = response["content"]
            result = json.loads(response_content)

            score = float(result.get("score", 0.0))
            explanation = result.get("explanation", "No explanation provided")

            # Clamp score to [0.0, 1.0]
            score = max(0.0, min(1.0, score))

            logger.debug(
                f"Faithfulness score: {score:.2f} - {explanation}"
            )

            return score, explanation

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM judge response: {e}")
            return 0.0, f"Error parsing judge response: {str(e)}"

        except Exception as e:
            logger.error(f"Error in faithfulness evaluation: {e}")
            return 0.0, f"Evaluation error: {str(e)}"


# Global instances
tool_selection_evaluator = ToolSelectionEvaluator()
argument_match_evaluator = ArgumentMatchEvaluator()
faithfulness_evaluator = ResponseFaithfulnessEvaluator()
