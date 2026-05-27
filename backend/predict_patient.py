"""
Predict patient risk using both the old and new models.
Can be run with custom inputs as command-line arguments or prints standard patient examples.
"""

import sys
import json
import pickle
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ARTIFACTS_DIR = BASE_DIR / "ml" / "artifacts"
OLD_ARTIFACTS_DIR = ARTIFACTS_DIR / "old_backup"

FEATURE_ORDER = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
    "thalach", "exang", "oldpeak", "slope", "ca", "thal"
]

def old_custom_scaling(prob: float) -> float:
    if prob < 0.2:
        return prob * 0.8
    elif prob < 0.4:
        return prob * 1.0
    elif prob < 0.6:
        return prob * 1.2
    elif prob < 0.8:
        return min(1.0, prob * 1.3)
    else:
        return min(1.0, prob * 1.4)

def get_risk_level_old(score: float) -> str:
    if score > 50:
        return "High"
    elif score > 20:
        return "Moderate"
    else:
        return "Low"

def get_risk_level_new(score: float) -> str:
    if score > 60:
        return "High"
    elif score > 30:
        return "Moderate"
    else:
        return "Low"

def load_models():
    # Load old model
    with open(OLD_ARTIFACTS_DIR / "xgb_model_old.pkl", "rb") as f:
        old_model = pickle.load(f)
    with open(OLD_ARTIFACTS_DIR / "scaler_old.pkl", "rb") as f:
        old_scaler = pickle.load(f)
    
    # Load new model
    with open(ARTIFACTS_DIR / "xgb_model.pkl", "rb") as f:
        new_model = pickle.load(f)
    with open(ARTIFACTS_DIR / "scaler.pkl", "rb") as f:
        new_scaler = pickle.load(f)
        
    return old_model, old_scaler, new_model, new_scaler

def predict_single(patient_data, old_model, old_scaler, new_model, new_scaler):
    df = pd.DataFrame([patient_data]).reindex(columns=FEATURE_ORDER).astype(float)
    
    # Old model prediction
    old_scaled = old_scaler.transform(df)
    old_raw = float(old_model.predict_proba(old_scaled)[0][1])
    old_scaled_prob = old_custom_scaling(old_raw)
    old_pct = round(old_scaled_prob * 100, 2)
    old_lvl = get_risk_level_old(old_pct)
    
    # New model prediction
    new_scaled = new_scaler.transform(df)
    new_prob = float(new_model.predict_proba(new_scaled)[0][1])
    new_pct = round(new_prob * 100, 2)
    new_lvl = get_risk_level_new(new_pct)
    
    return {
        "old_raw": round(old_raw * 100, 2),
        "old_scaled": old_pct,
        "old_level": old_lvl,
        "new_prob": new_pct,
        "new_level": new_lvl
    }

def main():
    old_model, old_scaler, new_model, new_scaler = load_models()
    
    if len(sys.argv) > 1:
        try:
            # Parse patient data JSON from first argument
            patient_data = json.loads(sys.argv[1])
            res = predict_single(patient_data, old_model, old_scaler, new_model, new_scaler)
            print(json.dumps(res, indent=2))
            return
        except Exception as e:
            print(f"Error parsing input or predicting: {e}", file=sys.stderr)
            sys.exit(1)
            
    # Default cases if no argument provided
    default_cases = {
        "High Risk Patient (Typical Chest Pain, Older, Low Max Heart Rate)": {
            "age": 63, "sex": 1, "cp": 3, "trestbps": 145, "chol": 233, "fbs": 1,
            "restecg": 0, "thalach": 150, "exang": 0, "oldpeak": 2.3, "slope": 0,
            "ca": 0, "thal": 1
        },
        "Low Risk Patient (Non-Anginal, Younger, High Max Heart Rate)": {
            "age": 37, "sex": 1, "cp": 2, "trestbps": 130, "chol": 250, "fbs": 0,
            "restecg": 1, "thalach": 187, "exang": 0, "oldpeak": 3.5, "slope": 0,
            "ca": 0, "thal": 2
        },
        "Moderate Risk Patient": {
            "age": 54, "sex": 0, "cp": 1, "trestbps": 140, "chol": 230, "fbs": 0,
            "restecg": 1, "thalach": 160, "exang": 0, "oldpeak": 1.2, "slope": 2,
            "ca": 0, "thal": 2
        }
    }
    
    for name, data in default_cases.items():
        res = predict_single(data, old_model, old_scaler, new_model, new_scaler)
        print(f"\n--- {name} ---")
        print(f"Inputs: {data}")
        print(f"Old Model Prediction (with custom scaling): {res['old_scaled']}% ({res['old_level']})  [Raw: {res['old_raw']}%]")
        print(f"New Model Prediction (calibrated):          {res['new_prob']}% ({res['new_level']})")

if __name__ == "__main__":
    main()
