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

    expected_tool = row.get('expected_tool', '').strip()
    if not expected_tool:
        raise ValueError("expected_tool cannot be empty")

    expected_args_str = row.get('expected_args', '').strip()
    if not expected_args_str:
        raise ValueError("expected_args cannot be empty")

    expected_response_contains = row.get('expected_response_contains', '').strip()
    if not expected_response_contains:
        raise ValueError("expected_response_contains cannot be empty")

    # Parse expected_args as JSON
    try:
        expected_args = json.loads(expected_args_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"expected_args must be valid JSON: {str(e)}")

    if not isinstance(expected_args, dict):
        raise ValueError("expected_args must be a JSON object (dict), not a list or primitive")

    # Create TestCase object
    return TestCase(
        test_id=test_id,
        query=query,
        expected_tool=expected_tool,
        expected_args=expected_args,
        expected_response_contains=expected_response_contains
    )
