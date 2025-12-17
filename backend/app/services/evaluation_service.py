"""Evaluation service for orchestrating test case execution and evaluation."""

import logging
from typing import List, Dict, Any, AsyncIterator
from app.schemas.evaluation import (
    TestCase,
    EvaluationResult,
    EvaluationSummary,
    MetricScore,
    StatusEvent,
    TestCaseStartEvent,
    ErrorEvent
)
from app.services.agent_service import agent_service
from app.services.evaluation_metrics import (
    tool_selection_evaluator,
    argument_match_evaluator,
    faithfulness_evaluator
)
from app.tools.base import tool_registry
from app.prompts.prompt_utils import render_prompt

logger = logging.getLogger(__name__)


class EvaluationService:
    """Service for running evaluations on test cases."""

    def __init__(self):
        self.agent_service = agent_service
        self.pass_threshold = 0.7  # Overall score threshold for passing

    async def run_evaluation(
        self,
        test_cases: List[TestCase]
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream evaluation results for all test cases.

        Yields:
            SSE event dictionaries
        """
        total_tests = len(test_cases)
        results = []

        # Initial status
        yield StatusEvent(
            message=f"Loaded {total_tests} test cases",
            progress=0
        ).model_dump()

        # Evaluate each test case
        for idx, test_case in enumerate(test_cases, start=1):
            # Emit test_case_start event
            yield TestCaseStartEvent(
                test_id=test_case.test_id,
                query=test_case.query,
                current=idx,
                total=total_tests
            ).model_dump()

            try:
                # Evaluate test case
                result = await self.evaluate_test_case(test_case)
                results.append(result)

                # Emit test_case_result event
                yield {
                    "type": "test_case_result",
                    **result.model_dump()
                }

                # Progress update
                progress = int((idx / total_tests) * 100)
                yield StatusEvent(
                    message=f"Completed {idx}/{total_tests} tests",
                    progress=progress
                ).model_dump()

            except Exception as e:
                logger.error(f"Error evaluating test case {test_case.test_id}: {e}")
                yield ErrorEvent(
                    test_id=test_case.test_id,
                    message=f"Failed to evaluate: {str(e)}",
                    continue_evaluation=True
                ).model_dump()

        # Compute summary
        summary = self._compute_summary(results)
        yield {
            "type": "summary",
            **summary.model_dump()
        }

        # Final completion status
        yield StatusEvent(
            message="Evaluation complete",
            progress=100
        ).model_dump()

    async def evaluate_test_case(
        self,
        test_case: TestCase
    ) -> EvaluationResult:
        """
        Evaluate a single test case.

        Args:
            test_case: Test case to evaluate

        Returns:
            EvaluationResult with metrics
        """
        logger.info(f"Evaluating test case: {test_case.test_id}")

        # Run agent with test query
        system_prompt = render_prompt("fin_react_agent")
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": test_case.query}
        ]

        agent_result = await self.agent_service.execute_agent(messages=messages)

        # Extract tool calls and final response
        tool_executions = agent_result.get("tool_executions", [])
        final_response = agent_result.get("content", "")

        # Extract actual tools (map display names to internal names)
        actual_tools = []
        actual_tool_args = {}
        tool_outputs = []

        for exec in tool_executions:
            display_name = exec.get("tool_name", "")
            tool_input = exec.get("tool_input", {})
            tool_output = exec.get("tool_output", "")

            # Map display name to internal name
            internal_name = self._get_internal_tool_name(display_name)
            actual_tools.append(internal_name)

            # Store arguments for the expected tool
            if internal_name == test_case.expected_tool:
                actual_tool_args = tool_input

            # Collect tool outputs for faithfulness check
            tool_outputs.append(f"{display_name}: {tool_output}")

        # Run evaluators
        metrics = []

        # 1. Tool Selection
        tool_selection_score = tool_selection_evaluator.evaluate(
            test_case.expected_tool,
            actual_tools
        )
        metrics.append(MetricScore(
            metric_name="tool_selection",
            score=tool_selection_score
        ))

        # 2. Argument Match
        argument_match_score = argument_match_evaluator.evaluate(
            test_case.expected_args,
            actual_tool_args
        )
        metrics.append(MetricScore(
            metric_name="argument_match",
            score=argument_match_score
        ))

        # 3. Response Faithfulness
        faithfulness_score, explanation = await faithfulness_evaluator.evaluate(
            query=test_case.query,
            expected_contains=test_case.expected_response_contains,
            actual_response=final_response,
            tool_outputs=tool_outputs
        )
        metrics.append(MetricScore(
            metric_name="faithfulness",
            score=faithfulness_score,
            details=explanation
        ))

        # Compute overall score
        overall_score = sum(m.score for m in metrics) / len(metrics)
        passed = overall_score >= self.pass_threshold

        return EvaluationResult(
            test_id=test_case.test_id,
            query=test_case.query,
            expected_tool=test_case.expected_tool,
            actual_tools=actual_tools,
            actual_response=final_response,
            metrics=metrics,
            overall_score=overall_score,
            passed=passed
        )

    def _get_internal_tool_name(self, display_name: str) -> str:
        """
        Map tool display name to internal name.

        Args:
            display_name: Human-readable tool name (e.g., "Stock Price Lookup")

        Returns:
            Internal tool name (e.g., "get_stock_price")
        """
        for tool in tool_registry.get_all_tools():
            if tool.get_display_name() == display_name:
                return tool.name

        # Fallback: convert to snake_case
        return display_name.lower().replace(" ", "_")

    def _compute_summary(self, results: List[EvaluationResult]) -> EvaluationSummary:
        """
        Compute aggregated summary metrics.

        Args:
            results: List of evaluation results

        Returns:
            EvaluationSummary with aggregated metrics
        """
        if not results:
            return EvaluationSummary(
                total_tests=0,
                passed=0,
                failed=0,
                average_tool_selection=0.0,
                average_argument_match=0.0,
                average_faithfulness=0.0,
                overall_average=0.0
            )

        total_tests = len(results)
        passed = sum(1 for r in results if r.passed)
        failed = total_tests - passed

        # Aggregate metric scores
        tool_selection_scores = []
        argument_match_scores = []
        faithfulness_scores = []

        for result in results:
            for metric in result.metrics:
                if metric.metric_name == "tool_selection":
                    tool_selection_scores.append(metric.score)
                elif metric.metric_name == "argument_match":
                    argument_match_scores.append(metric.score)
                elif metric.metric_name == "faithfulness":
                    faithfulness_scores.append(metric.score)

        avg_tool_selection = (
            sum(tool_selection_scores) / len(tool_selection_scores)
            if tool_selection_scores else 0.0
        )
        avg_argument_match = (
            sum(argument_match_scores) / len(argument_match_scores)
            if argument_match_scores else 0.0
        )
        avg_faithfulness = (
            sum(faithfulness_scores) / len(faithfulness_scores)
            if faithfulness_scores else 0.0
        )

        overall_average = (
            avg_tool_selection + avg_argument_match + avg_faithfulness
        ) / 3

        return EvaluationSummary(
            total_tests=total_tests,
            passed=passed,
            failed=failed,
            average_tool_selection=avg_tool_selection,
            average_argument_match=avg_argument_match,
            average_faithfulness=avg_faithfulness,
            overall_average=overall_average
        )


# Global instance
evaluation_service = EvaluationService()
