"""Evaluator classes for computing evaluation metrics."""

import json
import logging
import re
from typing import Dict, Any, List, Tuple, Optional, Union
from app.services.openai_service import openai_service
from app.prompts.prompt_utils import render_prompt

logger = logging.getLogger(__name__)


def _extract_json_from_response(content: str) -> Optional[Dict[str, Any]]:
    """Extract JSON from LLM response, handling markdown code blocks."""
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
            return json.loads(match)
        except json.JSONDecodeError:
            continue

    return None


class ToolSelectionEvaluator:
    """
    Evaluates whether the agent selected the correct tool(s).

    Scoring:
    - Single tool: 1.0 if expected tool was called, 0.0 otherwise
    - Multiple tools: Percentage of expected tools that were called
    """

    def evaluate(self, expected_tool: Union[str, List[str]], actual_tools: List[str]) -> float:
        """
        Evaluate tool selection accuracy.

        Args:
            expected_tool: Internal name(s) of expected tool(s) - string or list
            actual_tools: List of internal names of tools actually called

        Returns:
            For single tool: 1.0 if expected tool in actual_tools, else 0.0
            For multiple tools: % of expected tools found (0.0-1.0)
        """
        # Convert to list if single tool
        expected_tools = [expected_tool] if isinstance(expected_tool, str) else expected_tool

        # Count how many expected tools were actually called
        found_count = sum(1 for tool in expected_tools if tool in actual_tools)
        score = found_count / len(expected_tools)

        if score == 1.0:
            logger.debug(
                f"Tool selection PASS: expected {expected_tools}, "
                f"actual {actual_tools}"
            )
        else:
            missing = [t for t in expected_tools if t not in actual_tools]
            logger.debug(
                f"Tool selection PARTIAL/FAIL: expected {expected_tools}, "
                f"actual {actual_tools}, missing {missing}, score {score:.2f}"
            )

        return score


class ArgumentMatchEvaluator:
    """
    Evaluates whether tool arguments match expected values.

    Scoring:
    - Single tool: 0.0-1.0 based on percentage of matching fields
    - Multiple tools: Average score across all tools
    """

    def evaluate(
        self,
        expected_args: Union[Dict[str, Any], List[Dict[str, Any]]],
        actual_args_list: List[Dict[str, Any]]
    ) -> float:
        """
        Evaluate argument match accuracy.

        Args:
            expected_args: Dictionary or list of dictionaries for expected arguments
            actual_args_list: List of actual argument dictionaries (one per expected tool)

        Returns:
            Score from 0.0 to 1.0 based on field-level comparison
        """
        # Convert to list if single dict
        expected_args_list = [expected_args] if isinstance(expected_args, dict) else expected_args

        if len(actual_args_list) != len(expected_args_list):
            logger.warning(
                f"Argument count mismatch: expected {len(expected_args_list)}, "
                f"got {len(actual_args_list)}"
            )
            # Pad or truncate to match lengths
            actual_args_list = (actual_args_list + [{}] * len(expected_args_list))[:len(expected_args_list)]

        # Evaluate each tool's arguments
        scores = []
        for i, (expected, actual) in enumerate(zip(expected_args_list, actual_args_list)):
            score = self._evaluate_single_tool_args(expected, actual, tool_index=i)
            scores.append(score)

        # Return average score
        overall_score = sum(scores) / len(scores) if scores else 0.0
        logger.debug(f"Overall argument match score: {overall_score:.2f} (avg of {scores})")
        return overall_score

    def _evaluate_single_tool_args(
        self,
        expected_args: Dict[str, Any],
        actual_args: Dict[str, Any],
        tool_index: int = 0
    ) -> float:
        """
        Evaluate argument match for a single tool.

        Args:
            expected_args: Dictionary of expected arguments
            actual_args: Dictionary of actual arguments
            tool_index: Index of tool being evaluated (for logging)

        Returns:
            Score from 0.0 to 1.0
        """
        if not expected_args:
            # If no expected args, perfect match
            return 1.0

        if not actual_args:
            # If expected args but no actual args, fail
            logger.debug(f"Tool {tool_index}: Argument match FAIL - no actual arguments provided")
            return 0.0

        matching_fields = 0
        total_fields = len(expected_args)

        for key, expected_value in expected_args.items():
            actual_value = actual_args.get(key)

            if actual_value is None:
                logger.debug(f"Tool {tool_index}: missing field '{key}'")
                continue

            if self._values_match(expected_value, actual_value):
                matching_fields += 1
                logger.debug(
                    f"Tool {tool_index}: field '{key}' matches "
                    f"(expected={expected_value}, actual={actual_value})"
                )
            else:
                logger.debug(
                    f"Tool {tool_index}: field '{key}' mismatch "
                    f"(expected={expected_value}, actual={actual_value})"
                )

        score = matching_fields / total_fields
        logger.debug(
            f"Tool {tool_index}: Argument match score: {score:.2f} "
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

            # Parse JSON response (same pattern as agent_service)
            response_content = response.choices[0].message.content or ""
            result = _extract_json_from_response(response_content)

            if not result:
                logger.error(f"Failed to extract JSON from LLM judge response: {response_content[:200]}")
                return 0.0, f"Invalid judge response format"

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
