"""ML model loading and prediction — singleton pattern with calibrated probabilities."""

import logging
import pickle
from pathlib import Path
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)

_model = None
_scaler = None

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

ARTIFACTS_DIR = Path(__file__).parent / "artifacts"


def load_model() -> None:
    """Load the XGBoost model and StandardScaler from disk."""
    global _model, _scaler

    model_path = ARTIFACTS_DIR / "xgb_model.pkl"
    scaler_path = ARTIFACTS_DIR / "scaler.pkl"

    with open(model_path, "rb") as f:
        _model = pickle.load(f)
    logger.info("XGBoost model loaded from %s", model_path)

    with open(scaler_path, "rb") as f:
        _scaler = pickle.load(f)
    logger.info("StandardScaler loaded from %s", scaler_path)


def predict(input_data: dict[str, Any]) -> tuple[float, str]:
    """
    Run a prediction and return (risk_score_percentage, risk_level).

    The risk_score_percentage is 0-100. risk_level is one of
    'Low', 'Moderate', or 'High'.

    The model outputs calibrated probabilities directly (via isotonic
    calibration during training), so no post-hoc scaling is needed.
    """
    if _model is None or _scaler is None:
        raise RuntimeError("Model not loaded — call load_model() first")

    df = pd.DataFrame([input_data]).reindex(columns=FEATURE_ORDER)
    df = df.astype(float)
    scaled = _scaler.transform(df)

    prob = float(_model.predict_proba(scaled)[0][1])
    risk_score = round(prob * 100, 2)

    if risk_score > 60:
        risk_level = "High"
    elif risk_score > 30:
        risk_level = "Moderate"
    else:
        risk_level = "Low"

    return risk_score, risk_level


