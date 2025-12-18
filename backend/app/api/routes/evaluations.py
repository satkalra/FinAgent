"""Evaluation API endpoints for uploading test datasets and streaming results."""

import logging

from app.core.sse_manager import sse_manager
from app.services.evaluation_service import evaluation_service
from app.utils.csv_parser import CSVParseError, parse_evaluation_csv
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)

router = APIRouter()

# Configuration
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_TEST_CASES = 100


@router.post("/run")
async def run_evaluation(file: UploadFile = File(...)):
    """
    Upload CSV file and stream evaluation results via SSE.

    Args:
        file: CSV file with test cases

    Returns:
        StreamingResponse with SSE events

    SSE Event Types:
    - status: Progress updates
    - test_case_start: Starting a test case
    - test_case_result: Individual test result
    - summary: Final aggregated metrics
    - error: Error events
    """
    # Validate file extension
    if not file.filename or not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="File must be a CSV file (.csv extension)"
        )

    # Read file content
    try:
        content = await file.read()
    except Exception as e:
        logger.error("Error reading uploaded file: %e", e)
        raise HTTPException(
            status_code=400,
            detail=f"Failed to read file: {str(e)}"
        ) from e

    # Check file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE / (1024*1024):.1f}MB"
        )

    # Parse CSV
    try:
        test_cases = parse_evaluation_csv(content)
    except CSVParseError as e:
        logger.error("CSV parsing error: %e", e)
        raise HTTPException(
            status_code=400,
            detail=f"Invalid CSV format: {str(e)}"
        ) from e

    # Check test case limit
    if len(test_cases) > MAX_TEST_CASES:
        raise HTTPException(
            status_code=400,
            detail=f"Too many test cases. Maximum is {MAX_TEST_CASES}, got {len(test_cases)}"
        )

    # Stream evaluation results
    async def event_generator():
        """Generate SSE events for evaluation progress."""
        try:
            async for event in evaluation_service.run_evaluation(test_cases):
                event_type = event.get("type", "status")
                yield sse_manager.format_sse(event, event=event_type)

        except Exception as e:
            logger.error("Error during evaluation: %s", e)
            yield sse_manager.format_sse(
                {
                    "type": "error",
                    "message": f"Evaluation failed: {str(e)}",
                    "continue": False
                },
                event="error"
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )
