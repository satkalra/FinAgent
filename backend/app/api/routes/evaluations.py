"""Evaluation API endpoints."""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.schemas.evaluation import (
    EvaluationCreate,
    EvaluationUpdate,
    EvaluationResponse,
)
from app.models import Evaluation

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("", response_model=EvaluationResponse, status_code=201)
async def create_evaluation(
    data: EvaluationCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create an evaluation for an AI response."""
    try:
        evaluation = Evaluation(**data.model_dump())
        db.add(evaluation)
        await db.commit()
        await db.refresh(evaluation)
        return evaluation
    except Exception as e:
        logger.error(f"Error creating evaluation: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=List[EvaluationResponse])
async def list_evaluations(
    message_id: int = Query(None),
    conversation_id: int = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List evaluations with optional filters."""
    try:
        query = select(Evaluation).order_by(Evaluation.created_at.desc())

        if message_id:
            query = query.where(Evaluation.message_id == message_id)
        if conversation_id:
            query = query.where(Evaluation.conversation_id == conversation_id)

        query = query.limit(limit).offset(offset)

        result = await db.execute(query)
        evaluations = list(result.scalars().all())
        return evaluations
    except Exception as e:
        logger.error(f"Error listing evaluations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{evaluation_id}", response_model=EvaluationResponse)
async def get_evaluation(
    evaluation_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get an evaluation by ID."""
    result = await db.execute(
        select(Evaluation).where(Evaluation.id == evaluation_id)
    )
    evaluation = result.scalar_one_or_none()

    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    return evaluation


@router.put("/{evaluation_id}", response_model=EvaluationResponse)
async def update_evaluation(
    evaluation_id: int,
    data: EvaluationUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an evaluation."""
    try:
        result = await db.execute(
            select(Evaluation).where(Evaluation.id == evaluation_id)
        )
        evaluation = result.scalar_one_or_none()

        if not evaluation:
            raise HTTPException(status_code=404, detail="Evaluation not found")

        # Update fields
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(evaluation, field, value)

        await db.commit()
        await db.refresh(evaluation)
        return evaluation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating evaluation: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{evaluation_id}", status_code=204)
async def delete_evaluation(
    evaluation_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete an evaluation."""
    try:
        result = await db.execute(
            select(Evaluation).where(Evaluation.id == evaluation_id)
        )
        evaluation = result.scalar_one_or_none()

        if not evaluation:
            raise HTTPException(status_code=404, detail="Evaluation not found")

        await db.delete(evaluation)
        await db.commit()
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting evaluation: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
