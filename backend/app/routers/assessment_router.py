import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Assessment, User
from app.schemas import AssessmentDetail, AssessmentSummary, MessageResponse, RecommendationItem

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/assessments", response_model=list[AssessmentSummary])
async def list_assessments(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[AssessmentSummary]:
    """Return all assessments for the current user, newest first."""
    result = await db.execute(
        select(Assessment)
        .where(Assessment.user_id == current_user.id)
        .order_by(Assessment.created_at.desc())
    )
    assessments = result.scalars().all()
    return [AssessmentSummary.model_validate(a) for a in assessments]


@router.get("/assessments/{assessment_id}", response_model=AssessmentDetail)
async def get_assessment(
    assessment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AssessmentDetail:
    """Return a single assessment with full details."""
    result = await db.execute(
        select(Assessment).where(Assessment.id == assessment_id)
    )
    assessment = result.scalar_one_or_none()

    if assessment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")

    if assessment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return AssessmentDetail(
        id=assessment.id,
        risk_score=assessment.risk_score,
        risk_level=assessment.risk_level,
        created_at=assessment.created_at,
        input_data=assessment.input_data,
        recommendations=[RecommendationItem(**r) for r in assessment.recommendations],
    )


@router.delete("/assessments/{assessment_id}", response_model=MessageResponse)
async def delete_assessment(
    assessment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Delete an assessment owned by the current user."""
    result = await db.execute(
        select(Assessment).where(Assessment.id == assessment_id)
    )
    assessment = result.scalar_one_or_none()

    if assessment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")

    if assessment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    await db.delete(assessment)
    return MessageResponse(message="Assessment deleted successfully")
