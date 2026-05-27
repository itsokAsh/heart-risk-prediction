import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from io import BytesIO
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Assessment, User
from ml.report_generator import ReportGenerator
from ml.audio_generator import generate_audio_report

logger = logging.getLogger(__name__)

router = APIRouter()


async def _get_owned_assessment(
    assessment_id: uuid.UUID,
    current_user: User,
    db: AsyncSession,
) -> Assessment:
    """Fetch an assessment and verify ownership."""
    result = await db.execute(
        select(Assessment).where(Assessment.id == assessment_id)
    )
    assessment = result.scalar_one_or_none()

    if assessment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")

    if assessment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return assessment


@router.get("/reports/{assessment_id}/pdf")
async def download_pdf_report(
    assessment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate and return a PDF report for the given assessment."""
    assessment = await _get_owned_assessment(assessment_id, current_user, db)

    generator = ReportGenerator()
    pdf_bytes = generator.generate_report(
        personal_info=assessment.input_data,
        risk_score=assessment.risk_score,
        recommendations=assessment.recommendations,
    )

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=heart_report_{assessment_id}.pdf"},
    )


@router.get("/reports/{assessment_id}/audio")
async def download_audio_report(
    assessment_id: uuid.UUID,
    lang: str = Query(default="en"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate and return an audio report for the given assessment."""
    assessment = await _get_owned_assessment(assessment_id, current_user, db)

    try:
        audio_bytes = generate_audio_report(
            risk_score=assessment.risk_score,
            recommendations=assessment.recommendations,
            language_code=lang,
        )
    except Exception as exc:
        logger.exception("Audio generation failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audio generation failed: {str(exc)}",
        )

    return StreamingResponse(
        BytesIO(audio_bytes),
        media_type="audio/mpeg",
        headers={"Content-Disposition": f"attachment; filename=heart_report_{assessment_id}.mp3"},
    )
