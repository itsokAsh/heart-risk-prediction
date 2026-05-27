import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Assessment, User
from app.schemas import PredictionRequest, PredictionResponse, RecommendationItem
from ml.model import predict, predict_debug
from ml.recommendations import generate_health_recommendations

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/predict", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
async def run_prediction(
    body: PredictionRequest,
    debug: bool = Query(default=False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PredictionResponse:
    """Run a heart disease risk prediction and persist the assessment."""
    input_data = body.model_dump()

    risk_score, risk_level = predict(input_data)
    recommendations_raw = generate_health_recommendations(input_data, risk_score / 100.0)

    assessment = Assessment(
        user_id=current_user.id,
        input_data=input_data,
        risk_score=risk_score,
        risk_level=risk_level,
        recommendations=recommendations_raw,
    )
    db.add(assessment)
    await db.flush()
    await db.refresh(assessment)

    response = PredictionResponse(
        id=assessment.id,
        risk_score=assessment.risk_score,
        risk_level=assessment.risk_level,
        recommendations=[RecommendationItem(**r) for r in recommendations_raw],
        created_at=assessment.created_at,
    )

    if debug:
        debug_data = predict_debug(input_data)
        return response.model_copy(update={"debug": debug_data})

    return response
