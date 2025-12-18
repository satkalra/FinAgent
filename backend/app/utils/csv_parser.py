"""CSV parser and validator for evaluation test cases."""

import csv
import json
import io
import logging
from typing import List
from app.schemas.evaluation import TestCase

logger = logging.getLogger(__name__)


class CSVParseError(Exception):
    """Exception raised when CSV parsing fails."""
    pass


def parse_evaluation_csv(file_content: bytes) -> List[TestCase]:
    """
    Parse CSV file and return list of TestCase objects.

    Args:
        file_content: Raw bytes from uploaded CSV file

    Returns:
        List of TestCase objects

    Raises:
        CSVParseError: If CSV is malformed or validation fails
    """
    try:
        # Decode bytes to string
        content = file_content.decode('utf-8')
    except UnicodeDecodeError as e:
        raise CSVParseError(f"Invalid file encoding. Expected UTF-8: {str(e)}")

    # Parse CSV
    csv_reader = csv.DictReader(io.StringIO(content))

    # Validate required columns
    required_columns = {
        'test_id',
        'query',
        'expected_tool',
        'expected_args',
        'expected_response_contains'
    }

    if not csv_reader.fieldnames:
        raise CSVParseError("CSV file is empty or has no header row")

    missing_columns = required_columns - set(csv_reader.fieldnames)
    if missing_columns:
        raise CSVParseError(
            f"Missing required columns: {', '.join(sorted(missing_columns))}"
        )

    test_cases = []
    seen_ids = set()
    line_num = 1  # Header is line 1

    for row_dict in csv_reader:
        line_num += 1

        try:
            test_case = validate_test_case(row_dict, line_num)

            # Check for duplicate test_ids
            if test_case.test_id in seen_ids:
                raise CSVParseError(
                    f"Line {line_num}: Duplicate test_id '{test_case.test_id}'"
                )

            seen_ids.add(test_case.test_id)
            test_cases.append(test_case)

        except (ValueError, json.JSONDecodeError) as e:
            raise CSVParseError(f"Line {line_num}: {str(e)}")

    if not test_cases:
        raise CSVParseError("CSV file contains no valid test cases")

    logger.info(f"Successfully parsed {len(test_cases)} test cases from CSV")
    return test_cases


def validate_test_case(row: dict, line_num: int) -> TestCase:
    """
    Validate and convert CSV row to TestCase object.

    Args:
        row: Dictionary from CSV row
        line_num: Line number for error messages

    Returns:
        TestCase object

    Raises:
        ValueError: If validation fails
        json.JSONDecodeError: If expected_args is not valid JSON
    """
    # Check for empty values
    test_id = row.get('test_id', '').strip()
    if not test_id:
        raise ValueError("test_id cannot be empty")

    query = row.get('query', '').strip()
    if not query:
        raise ValueError("query cannot be empty")

    expected_tool_str = row.get('expected_tool', '').strip()
    if not expected_tool_str:
        raise ValueError("expected_tool cannot be empty")

    expected_args_str = row.get('expected_args', '').strip()
    if not expected_args_str:
        raise ValueError("expected_args cannot be empty")

    expected_response_contains = row.get('expected_response_contains', '').strip()
    if not expected_response_contains:
        raise ValueError("expected_response_contains cannot be empty")

    # Parse expected_tool - can be string or JSON array
    expected_tool = expected_tool_str
    if expected_tool_str.startswith('['):
        # Parse as JSON array
        try:
            expected_tool = json.loads(expected_tool_str)
            if not isinstance(expected_tool, list):
                raise ValueError("expected_tool array must be a JSON array")
            if not all(isinstance(t, str) for t in expected_tool):
                raise ValueError("All items in expected_tool array must be strings")
            if len(expected_tool) == 0:
                raise ValueError("expected_tool array cannot be empty")
        except json.JSONDecodeError as e:
            raise ValueError(f"expected_tool array must be valid JSON: {str(e)}")

    # Parse expected_args - can be dict or JSON array of dicts
    try:
        expected_args = json.loads(expected_args_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"expected_args must be valid JSON: {str(e)}")

    # Validate expected_args structure
    if isinstance(expected_args, dict):
        # Single dict is valid
        pass
    elif isinstance(expected_args, list):
        # List of dicts
        if len(expected_args) == 0:
            raise ValueError("expected_args array cannot be empty")
        if not all(isinstance(arg, dict) for arg in expected_args):
            raise ValueError("All items in expected_args array must be JSON objects (dicts)")
    else:
        raise ValueError("expected_args must be a JSON object or array of objects")

    # Validate that tool and args structures match
    is_tool_list = isinstance(expected_tool, list)
    is_args_list = isinstance(expected_args, list)

    if is_tool_list != is_args_list:
        raise ValueError(
            "expected_tool and expected_args must both be single values or both be arrays"
        )

    if is_tool_list and is_args_list and len(expected_tool) != len(expected_args):
        raise ValueError(
            f"Number of tools ({len(expected_tool)}) must match number of arg objects ({len(expected_args)})"
        )

    # Create TestCase object
    return TestCase(
        test_id=test_id,
        query=query,
        expected_tool=expected_tool,
        expected_args=expected_args,
        expected_response_contains=expected_response_contains
    )
