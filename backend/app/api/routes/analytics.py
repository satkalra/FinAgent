"""Analytics API endpoints."""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.schemas.analytics import AnalyticsOverview, ToolUsageStats, QualityMetrics
from app.models import Conversation, Message, Evaluation, ToolExecution
from typing import List

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/overview", response_model=AnalyticsOverview)
async def get_analytics_overview(
    db: AsyncSession = Depends(get_db),
):
    """Get overall analytics overview."""
    try:
        # Total conversations
        total_conversations = await db.scalar(
            select(func.count()).select_from(Conversation)
        )

        # Total messages
        total_messages = await db.scalar(
            select(func.count()).select_from(Message)
        )

        # Total evaluations
        total_evaluations = await db.scalar(
            select(func.count()).select_from(Evaluation)
        )

        # Average rating
        avg_rating = await db.scalar(
            select(func.avg(Evaluation.rating))
        )

        # Average quality score
        avg_quality = await db.scalar(
            select(func.avg(Evaluation.quality_score))
        )

        # Total tokens
        total_tokens = await db.scalar(
            select(func.sum(Conversation.total_tokens))
        ) or 0

        # Average response time
        avg_response_time = await db.scalar(
            select(func.avg(Message.response_time_ms)).where(
                Message.response_time_ms.isnot(None)
            )
        )

        # Most used model
        most_used_model_result = await db.execute(
            select(Message.model_name, func.count(Message.model_name).label("count"))
            .where(Message.model_name.isnot(None))
            .group_by(Message.model_name)
            .order_by(func.count(Message.model_name).desc())
            .limit(1)
        )
        most_used_model_row = most_used_model_result.first()
        most_used_model = most_used_model_row[0] if most_used_model_row else None

        # Tool executions
        tool_executions = await db.scalar(
            select(func.count()).select_from(ToolExecution)
        )

        # Most used tool
        most_used_tool_result = await db.execute(
            select(ToolExecution.tool_name, func.count(ToolExecution.tool_name).label("count"))
            .group_by(ToolExecution.tool_name)
            .order_by(func.count(ToolExecution.tool_name).desc())
            .limit(1)
        )
        most_used_tool_row = most_used_tool_result.first()
        most_used_tool = most_used_tool_row[0] if most_used_tool_row else None

        return AnalyticsOverview(
            total_conversations=total_conversations or 0,
            total_messages=total_messages or 0,
            total_evaluations=total_evaluations or 0,
            average_rating=float(avg_rating) if avg_rating else None,
            average_quality_score=float(avg_quality) if avg_quality else None,
            total_tokens_used=total_tokens,
            average_response_time_ms=float(avg_response_time) if avg_response_time else None,
            most_used_model=most_used_model,
            tool_executions=tool_executions or 0,
            most_used_tool=most_used_tool,
        )

    except Exception as e:
        logger.error(f"Error getting analytics overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tool-usage", response_model=List[ToolUsageStats])
async def get_tool_usage_stats(
    db: AsyncSession = Depends(get_db),
):
    """Get tool usage statistics."""
    try:
        result = await db.execute(
            select(
                ToolExecution.tool_name,
                func.count(ToolExecution.id).label("execution_count"),
                func.sum(func.cast(ToolExecution.success, func.Integer)).label("success_count"),
                func.avg(ToolExecution.execution_time_ms).label("avg_time"),
            )
            .group_by(ToolExecution.tool_name)
            .order_by(func.count(ToolExecution.id).desc())
        )

        stats = []
        for row in result:
            stats.append(
                ToolUsageStats(
                    tool_name=row.tool_name,
                    execution_count=row.execution_count,
                    success_count=row.success_count or 0,
                    failure_count=row.execution_count - (row.success_count or 0),
                    average_execution_time_ms=float(row.avg_time) if row.avg_time else None,
                )
            )

        return stats

    except Exception as e:
        logger.error(f"Error getting tool usage stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quality-metrics", response_model=QualityMetrics)
async def get_quality_metrics(
    db: AsyncSession = Depends(get_db),
):
    """Get aggregated quality metrics."""
    try:
        result = await db.execute(
            select(
                func.avg(Evaluation.rating).label("avg_rating"),
                func.avg(Evaluation.quality_score).label("avg_quality"),
                func.avg(Evaluation.accuracy_score).label("avg_accuracy"),
                func.avg(Evaluation.relevance_score).label("avg_relevance"),
                func.avg(Evaluation.helpfulness_score).label("avg_helpfulness"),
                func.avg(Evaluation.tool_usage_quality).label("avg_tool_quality"),
                func.count(Evaluation.id).label("total"),
            )
        )

        row = result.first()

        return QualityMetrics(
            average_rating=float(row.avg_rating) if row.avg_rating else None,
            average_quality_score=float(row.avg_quality) if row.avg_quality else None,
            average_accuracy_score=float(row.avg_accuracy) if row.avg_accuracy else None,
            average_relevance_score=float(row.avg_relevance) if row.avg_relevance else None,
            average_helpfulness_score=float(row.avg_helpfulness) if row.avg_helpfulness else None,
            average_tool_usage_quality=float(row.avg_tool_quality) if row.avg_tool_quality else None,
            total_evaluations=row.total or 0,
        )

    except Exception as e:
        logger.error(f"Error getting quality metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
