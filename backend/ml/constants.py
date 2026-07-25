"""Shared constants for risk assessment thresholds and feature definitions.

All modules that classify risk levels or generate reports must import
thresholds from here to guarantee consistency across predictions,
PDF reports, audio reports, and recommendations.
"""

# Risk level thresholds (applied to 0-100 percentage scores)
HIGH_RISK_THRESHOLD = 60    # score > 60 → High
MODERATE_RISK_THRESHOLD = 30  # score > 30 → Moderate
# score ≤ 30 → Low

# Risk level labels
RISK_HIGH = "High"
RISK_MODERATE = "Moderate"
RISK_LOW = "Low"


def classify_risk(score_pct: float) -> str:
    """Classify a 0-100 risk score into a risk level string.

    Args:
        score_pct: Risk score as a percentage (0-100).

    Returns:
        One of 'High', 'Moderate', or 'Low'.
    """
    if score_pct > HIGH_RISK_THRESHOLD:
        return RISK_HIGH
    elif score_pct > MODERATE_RISK_THRESHOLD:
        return RISK_MODERATE
    else:
        return RISK_LOW


# Canonical feature order for the XGBoost model
FEATURE_ORDER = [
    "age",
    "sex",
    "cp",
    "trestbps",
    "chol",
    "fbs",
    "restecg",
    "thalach",
    "exang",
    "oldpeak",
    "slope",
    "ca",
    "thal",
]

# Recommendation category names (with emoji prefixes as used by recommendations.py)
CATEGORY_IMMEDIATE = "🚨 Immediate Actions Required"
CATEGORY_PREVENTIVE = "✅ Preventive Measures"
CATEGORY_LIFESTYLE = "💪 Lifestyle Modifications"
CATEGORY_DIET = "🥗 Dietary Guidelines"
CATEGORY_EXERCISE = "🏃‍♂️ Physical Activity Plan"

# Categories whose steps should be included in audio reports
AUDIO_INCLUDED_CATEGORIES = {
    CATEGORY_LIFESTYLE,
    CATEGORY_DIET,
    CATEGORY_EXERCISE,
}
