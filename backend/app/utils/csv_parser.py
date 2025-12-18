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
        raise CSVParseError(f"Invalid file encoding. Expected UTF-8: {str(e)}") from e

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
            # Parse JSON fields
            expected_tool_str = row_dict.get('expected_tool', '').strip()
            expected_args_str = row_dict.get('expected_args', '').strip()

            # Parse expected_tool (string or JSON array)
            if expected_tool_str.startswith('['):
                expected_tool = json.loads(expected_tool_str)
            else:
                expected_tool = expected_tool_str

            # Parse expected_args (dict or array of dicts)
            expected_args = json.loads(expected_args_str)

            # Prepare data for Pydantic validation
            test_data = {
                'test_id': row_dict.get('test_id', '').strip(),
                'query': row_dict.get('query', '').strip(),
                'expected_tool': expected_tool,
                'expected_args': expected_args,
                'expected_response_contains': row_dict.get('expected_response_contains', '').strip()
            }

            # Let Pydantic validate and create TestCase
            test_case = TestCase.model_validate(test_data)

            # Check for duplicate test_ids
            if test_case.test_id in seen_ids:
                raise ValueError(f"Duplicate test_id '{test_case.test_id}'")

            seen_ids.add(test_case.test_id)
            test_cases.append(test_case)

        except (ValueError, json.JSONDecodeError) as e:
            raise CSVParseError(f"Line {line_num}: {str(e)}") from e

    if not test_cases:
        raise CSVParseError("CSV file contains no valid test cases")

    logger.info("Successfully parsed %s test cases from CSV", len(test_cases))
    return test_cases
