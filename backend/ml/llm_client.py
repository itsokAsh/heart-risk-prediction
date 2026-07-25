"""LLM client abstraction for AI-powered health explanations.

Uses the Groq API (with Llama models) to generate personalized, context-aware
health explanations and recommendations based on assessment data.
"""

import logging
from typing import Any

from groq import AsyncGroq

from app.config import get_settings

logger = logging.getLogger(__name__)

# System prompt that grounds the LLM as a medical explanation assistant
SYSTEM_PROMPT = """\
You are HeartGuard AI, a knowledgeable and empathetic health assistant \
specializing in cardiovascular health education. Your role is to help \
patients understand their heart disease risk assessment results.

IMPORTANT RULES:
1. You are NOT a doctor. Always remind users to consult their physician.
2. Explain medical terms in simple, accessible language.
3. Be empathetic but honest about risk levels.
4. Ground your explanations in the specific assessment data provided.
5. When discussing risk factors, explain WHY they matter for heart health.
6. Keep responses concise (2-4 paragraphs) unless asked for more detail.
7. Never diagnose conditions or prescribe medications.
8. If asked about something outside cardiovascular health, politely redirect.
"""

# Default Groq model — fast inference, strong reasoning
GROQ_MODEL = "llama-3.3-70b-versatile"

FEATURE_LABELS = {
    "age": "Age",
    "sex": ("Female", "Male"),
    "cp": ("Typical Angina", "Atypical Angina", "Non-Anginal Pain", "Asymptomatic"),
    "trestbps": "Resting Blood Pressure (mm Hg)",
    "chol": "Serum Cholesterol (mg/dL)",
    "fbs": ("No", "Yes"),
    "restecg": ("Normal", "ST-T Wave Abnormality", "Left Ventricular Hypertrophy"),
    "thalach": "Maximum Heart Rate Achieved",
    "exang": ("No", "Yes"),
    "oldpeak": "ST Depression (Oldpeak)",
    "slope": ("Upsloping", "Flat", "Downsloping"),
    "ca": "Number of Major Vessels (0-3)",
    "thal": {1: "Normal", 2: "Fixed Defect", 3: "Reversible Defect"},
}


def _format_assessment_context(
    input_data: dict[str, Any],
    risk_score: float,
    risk_level: str,
    recommendations: list[dict[str, Any]],
) -> str:
    """Format assessment data into a readable context block for the LLM."""
    lines = [
        f"PATIENT ASSESSMENT DATA:",
        f"  Risk Score: {risk_score}% ({risk_level} Risk)",
        f"  Clinical Inputs:",
    ]

    for key, value in input_data.items():
        label_info = FEATURE_LABELS.get(key, key)
        if isinstance(label_info, tuple):
            display_val = label_info[int(value)] if int(value) < len(label_info) else str(value)
            display_key = key.replace("_", " ").title()
        elif isinstance(label_info, dict):
            display_val = label_info.get(int(value), str(value))
            display_key = key.replace("_", " ").title()
        else:
            display_val = str(value)
            display_key = label_info
        lines.append(f"    {display_key}: {display_val}")

    lines.append("\n  Recommendations given:")
    for rec in recommendations:
        lines.append(f"    [{rec['category']}]")
        for step in rec["steps"][:3]:
            lines.append(f"      • {step}")

    return "\n".join(lines)


def _get_client() -> AsyncGroq:
    """Get a configured Groq async client instance."""
    settings = get_settings()
    if not settings.GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is not configured. "
            "Set it in your .env file to enable AI explanations."
        )
    return AsyncGroq(api_key=settings.GROQ_API_KEY)


async def explain_assessment(
    input_data: dict[str, Any],
    risk_score: float,
    risk_level: str,
    recommendations: list[dict[str, Any]],
    question: str | None = None,
) -> str:
    """Generate an AI-powered explanation of the assessment results.

    If a question is provided, the explanation will focus on answering it
    in the context of the assessment data. Otherwise, generates a general
    personalized summary.

    Args:
        input_data: The raw clinical input features.
        risk_score: The risk score as a percentage (0-100).
        risk_level: The risk classification ('Low', 'Moderate', 'High').
        recommendations: The generated recommendations list.
        question: Optional user question to answer.

    Returns:
        The AI-generated explanation text.
    """
    context = _format_assessment_context(input_data, risk_score, risk_level, recommendations)

    if question:
        user_prompt = (
            f"{context}\n\n"
            f"The patient is asking: \"{question}\"\n\n"
            f"Please answer their question based on the assessment data above. "
            f"Be specific to their actual values and risk factors."
        )
    else:
        user_prompt = (
            f"{context}\n\n"
            f"Please provide a personalized summary of this patient's heart health assessment. "
            f"Explain what their key risk factors are, why they matter, and what the most "
            f"important next steps should be. Synthesize all 13 clinical features together "
            f"rather than listing them individually. Be conversational and empathetic."
        )

    client = _get_client()
    response = await client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        max_tokens=1024,
    )
    return response.choices[0].message.content


async def chat_followup(
    input_data: dict[str, Any],
    risk_score: float,
    risk_level: str,
    recommendations: list[dict[str, Any]],
    conversation_history: list[dict[str, Any]],
    user_message: str,
) -> str:
    """Generate a conversational follow-up response in an ongoing chat.

    Maintains conversation context while keeping the assessment data
    grounded in the system context.

    Args:
        input_data: The raw clinical input features.
        risk_score: The risk score as a percentage (0-100).
        risk_level: The risk classification.
        recommendations: The generated recommendations list.
        conversation_history: List of {"role": "user"|"assistant", "content": text} dicts.
        user_message: The new message from the user.

    Returns:
        The AI-generated response text.
    """
    context = _format_assessment_context(input_data, risk_score, risk_level, recommendations)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Here is my heart health assessment:\n\n{context}"},
        {"role": "assistant", "content": "I've reviewed your assessment data. I'm here to help you understand your results and answer any questions. What would you like to know?"},
        *conversation_history,
        {"role": "user", "content": user_message},
    ]

    client = _get_client()
    response = await client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=1024,
    )
    return response.choices[0].message.content


async def generate_ai_narrative(
    input_data: dict[str, Any],
    risk_score: float,
    risk_level: str,
    recommendations: list[dict[str, Any]],
) -> str:
    """Generate a flowing narrative paragraph for PDF reports.

    Unlike explain_assessment, this is specifically formatted for inclusion
    in a PDF report — no markdown, no bullet points, just flowing prose.

    Returns:
        A 2-3 paragraph narrative suitable for a clinical report.
    """
    context = _format_assessment_context(input_data, risk_score, risk_level, recommendations)

    user_prompt = (
        f"{context}\n\n"
        f"Write a 2-3 paragraph personalized narrative summary of this patient's "
        f"heart health assessment for inclusion in a PDF report. "
        f"Requirements:\n"
        f"- Write in flowing prose, not bullet points or lists\n"
        f"- Synthesize all clinical features into a coherent story\n"
        f"- Explain the most significant risk factors and their interplay\n"
        f"- End with the single most important action the patient should take\n"
        f"- Do NOT use markdown formatting (no **, no #, no - lists)\n"
        f"- Keep a professional but warm tone suitable for a medical document\n"
        f"- Include the standard disclaimer that this is not medical advice"
    )

    client = _get_client()
    response = await client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.6,
        max_tokens=1024,
    )
    return response.choices[0].message.content


async def generate_audio_script(
    input_data: dict[str, Any],
    risk_score: float,
    risk_level: str,
    recommendations: list[dict[str, Any]],
    language_code: str = "en",
) -> str:
    """Generate a spoken audio script personalized for this specific patient.

    Explicitly references the patient's actual clinical numbers (blood pressure,
    cholesterol, etc.) and explains them in conversational spoken language.
    """
    context = _format_assessment_context(input_data, risk_score, risk_level, recommendations)

    prompt = (
        f"{context}\n\n"
        f"You are a warm, empathetic, and clear healthcare narrator recording a personalized audio "
        f"report for a patient. Write a script that will be read aloud by a text-to-speech engine.\n\n"
        f"Rules for spoken audio:\n"
        f"- Use short, clear, well-punctuated sentences so the TTS engine speaks with natural cadence and tone.\n"
        f"- Explicitly reference the patient's SPECIFIC clinical numbers (e.g., blood pressure, "
        f"cholesterol, max heart rate, chest pain type) and explain what their specific numbers mean in simple terms.\n"
        f"- Structure: Warm greeting -> Risk score summary ({risk_score}%, {risk_level} risk) -> Specific clinical factors driving the score -> "
        f"Top personalized action steps -> Encouraging closing with disclaimer.\n"
        f"- Do NOT use markdown symbols, bullet points, asterisks (*), or headers (#). Write purely spoken paragraphs.\n"
        f"- Keep the total length around 200-300 words.\n"
        f"- Write the entire script in language code '{language_code}'."
    )

    client = _get_client()
    response = await client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.6,
        max_tokens=1024,
    )
    return response.choices[0].message.content

