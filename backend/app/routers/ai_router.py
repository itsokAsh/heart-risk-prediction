"""AI explanation and chat endpoints — LLM-powered assessment insights."""

import logging
import uuid
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.limiter import limiter
from app.models import Assessment, User
from ml.llm_client import explain_assessment, chat_followup

logger = logging.getLogger(__name__)

router = APIRouter()


# --- Request / Response Schemas ---


class ExplainRequest(BaseModel):
    """Request body for the explain endpoint."""
    assessment_id: uuid.UUID
    question: str | None = Field(
        default=None,
        max_length=1000,
        description="Optional question to ask about the assessment. "
        "If omitted, a general personalized summary is generated.",
    )


class ExplainResponse(BaseModel):
    """Response from the AI explanation endpoint."""
    assessment_id: uuid.UUID
    explanation: str


class ChatMessage(BaseModel):
    """A single message in the conversation history."""
    role: Literal["user", "assistant"] = Field(description="Must be either 'user' or 'assistant'")
    content: str = Field(min_length=1, max_length=2000)


class ChatRequest(BaseModel):
    """Request body for the chat endpoint."""
    assessment_id: uuid.UUID
    message: str = Field(min_length=1, max_length=2000)
    history: list[ChatMessage] = Field(
        default_factory=list,
        max_length=10,
        description="Previous conversation messages for context (max 10).",
    )


class ChatResponse(BaseModel):
    """Response from the chat endpoint."""
    assessment_id: uuid.UUID
    reply: str


# --- Helpers ---


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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )

    if assessment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    return assessment


# --- Endpoints ---


@router.post("/explain", response_model=ExplainResponse)
@limiter.limit("10/minute")
async def explain(
    request: Request,
    body: ExplainRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ExplainResponse:
    """Generate an AI-powered explanation of an assessment.

    Optionally accepts a specific question to answer in the context
    of the assessment data. Without a question, generates a personalized
    health summary synthesizing all clinical features.
    """
    assessment = await _get_owned_assessment(body.assessment_id, current_user, db)

    try:
        explanation = await explain_assessment(
            input_data=assessment.input_data,
            risk_score=assessment.risk_score,
            risk_level=assessment.risk_level,
            recommendations=assessment.recommendations,
            question=body.question,
        )
    except RuntimeError as exc:
        logger.warning(f"AI explain configuration error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is not configured on the server.",
        )
    except Exception as exc:
        logger.exception("AI explanation failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI explanation service failed. Please try again later.",
        )

    return ExplainResponse(
        assessment_id=assessment.id,
        explanation=explanation,
    )


@router.post("/chat", response_model=ChatResponse)
@limiter.limit("10/minute")
async def chat(
    request: Request,
    body: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    """Conversational follow-up chat about an assessment.

    Maintains conversation context through the `history` field.
    The frontend should accumulate messages and send the full
    history with each request.
    """
    assessment = await _get_owned_assessment(body.assessment_id, current_user, db)

    # Convert ChatMessage objects to the format expected by the LLM client
    history = [
        {"role": msg.role, "content": msg.content}
        for msg in body.history
    ]

    try:
        reply = await chat_followup(
            input_data=assessment.input_data,
            risk_score=assessment.risk_score,
            risk_level=assessment.risk_level,
            recommendations=assessment.recommendations,
            conversation_history=history,
            user_message=body.message,
        )
    except RuntimeError as exc:
        logger.warning(f"AI chat configuration error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is not configured on the server.",
        )
    except Exception as exc:
        logger.exception("AI chat failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI chat service failed. Please try again later.",
        )

    return ChatResponse(
        assessment_id=assessment.id,
        reply=reply,
    )
