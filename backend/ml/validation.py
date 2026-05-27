"""Input validation constants and logic ported from the original utils.py."""

from typing import Any

FEATURE_RANGES = {
    "age": (29, 77),
    "trestbps": (94, 200),
    "chol": (126, 564),
    "thalach": (71, 202),
    "oldpeak": (0.0, 6.2),
}

CATEGORICAL_MAPPINGS = {
    "cp": {
        "Typical Angina": 0,
        "Atypical Angina": 1,
        "Non-Anginal Pain": 2,
        "Asymptomatic": 3,
    },
    "restecg": {
        "Normal": 0,
        "ST-T Wave Abnormality": 1,
        "Left Ventricular Hypertrophy": 2,
    },
    "slope": {
        "Upsloping": 0,
        "Flat": 1,
        "Downsloping": 2,
    },
    "thal": {
        "Normal": 1,
        "Fixed Defect": 2,
        "Reversible Defect": 3,
    },
    "sex": [0, 1],
    "fbs": [0, 1],
    "exang": [0, 1],
}

VALID_RANGES = {
    "age": (20, 100),
    "trestbps": (80, 200),
    "chol": (100, 600),
    "thalach": (60, 220),
    "oldpeak": (0.0, 10.0),
    "ca": (0, 4),
    "thal": (1, 3),
}


def validate_input(data: dict[str, Any]) -> dict[str, Any]:
    """Validate user input against predefined ranges and categories."""
    for field, (min_val, max_val) in VALID_RANGES.items():
        if field in data:
            value = data[field]
            if not (min_val <= value <= max_val):
                return {
                    "valid": False,
                    "message": f"{field.replace('_', ' ').title()} must be between {min_val} and {max_val}",
                }

    for field, valid_values in CATEGORICAL_MAPPINGS.items():
        if field in data:
            if isinstance(valid_values, dict):
                if data[field] not in valid_values.values():
                    return {
                        "valid": False,
                        "message": f"Invalid value for {field.replace('_', ' ').title()}",
                    }
            elif isinstance(valid_values, list):
                if data[field] not in valid_values:
                    return {
                        "valid": False,
                        "message": f"Invalid value for {field.replace('_', ' ').title()}",
                    }

    return {"valid": True, "message": "All inputs are valid"}
