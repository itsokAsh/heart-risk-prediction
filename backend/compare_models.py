"""
Compare old vs new model predictions side-by-side.
===================================================
Loads the backed-up old model and the newly trained model,
runs both on the heart.csv dataset and test cases, and prints
a comparison table.
"""

from pathlib import Path
import pickle
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "heart.csv"
ARTIFACTS_DIR = BASE_DIR / "ml" / "artifacts"
OLD_ARTIFACTS_DIR = ARTIFACTS_DIR / "old_backup"


def old_custom_scaling(prob: float) -> float:
    """The old custom_scaling function for reproducing old predictions."""
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


def load_artifacts(artifacts_dir: Path):
    """Load model and scaler from a directory."""
    with open(artifacts_dir / "xgb_model.pkl" if "old_backup" not in str(artifacts_dir)
              else artifacts_dir / "xgb_model_old.pkl", "rb") as f:
        model = pickle.load(f)
    with open(artifacts_dir / "scaler.pkl" if "old_backup" not in str(artifacts_dir)
              else artifacts_dir / "scaler_old.pkl", "rb") as f:
        scaler = pickle.load(f)
    return model, scaler


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


FEATURE_ORDER = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
    "thalach", "exang", "oldpeak", "slope", "ca", "thal",
]


def compare():
    # Load models
    print("Loading old model artifacts...")
    old_model, old_scaler = load_artifacts(OLD_ARTIFACTS_DIR)
    print("Loading new model artifacts...")
    new_model, new_scaler = load_artifacts(ARTIFACTS_DIR)

    # --- Test Cases ---
    test_cases = [
        {
            "name": "High Risk",
            "data": {
                "age": 58, "sex": 1, "cp": 1, "trestbps": 144,
                "chol": 256, "fbs": 1, "restecg": 1, "thalach": 115,
                "exang": 1, "oldpeak": 1.5, "slope": 1, "ca": 1, "thal": 3,
            },
        },
        {
            "name": "Low Risk",
            "data": {
                "age": 32, "sex": 0, "cp": 0, "trestbps": 115,
                "chol": 170, "fbs": 0, "restecg": 0, "thalach": 165,
                "exang": 0, "oldpeak": 0.1, "slope": 0, "ca": 0, "thal": 1,
            },
        },
        {
            "name": "Moderate Risk",
            "data": {
                "age": 52, "sex": 1, "cp": 2, "trestbps": 130,
                "chol": 230, "fbs": 0, "restecg": 1, "thalach": 155,
                "exang": 0, "oldpeak": 0.8, "slope": 2, "ca": 0, "thal": 2,
            },
        },
    ]

    print("\n" + "=" * 75)
    print("TEST CASE COMPARISON: Old Model vs New Model")
    print("=" * 75)
    print(f"{'Case':<16} {'Old Raw%':>9} {'Old Scaled%':>12} {'Old Level':>10}  │  {'New Score%':>10} {'New Level':>10}")
    print("-" * 75)

    for case in test_cases:
        df = pd.DataFrame([case["data"]]).reindex(columns=FEATURE_ORDER).astype(float)

        # Old model
        old_scaled = old_scaler.transform(df)
        old_raw = float(old_model.predict_proba(old_scaled)[0][1])
        old_final = old_custom_scaling(old_raw)
        old_pct = round(old_final * 100, 2)
        old_level = get_risk_level_old(old_pct)

        # New model
        new_scaled = new_scaler.transform(df)
        new_prob = float(new_model.predict_proba(new_scaled)[0][1])
        new_pct = round(new_prob * 100, 2)
        new_level = get_risk_level_new(new_pct)

        print(f"{case['name']:<16} {round(old_raw*100,2):>8}% {old_pct:>10}% {old_level:>10}  │  {new_pct:>9}% {new_level:>10}")

    # --- Dataset-wide comparison ---
    print("\n" + "=" * 75)
    print("DATASET-WIDE COMPARISON (first 20 rows of heart.csv)")
    print("=" * 75)

    df_all = pd.read_csv(DATA_PATH)
    X_all = df_all.drop("target", axis=1).reindex(columns=FEATURE_ORDER).astype(float)
    y_all = df_all["target"]

    old_probs_all = []
    new_probs_all = []

    for i in range(len(X_all)):
        row = X_all.iloc[[i]]

        old_s = old_scaler.transform(row)
        old_r = float(old_model.predict_proba(old_s)[0][1])
        old_f = old_custom_scaling(old_r)
        old_probs_all.append(old_f)

        new_s = new_scaler.transform(row)
        new_p = float(new_model.predict_proba(new_s)[0][1])
        new_probs_all.append(new_p)

    old_probs_all = np.array(old_probs_all)
    new_probs_all = np.array(new_probs_all)

    # Print first 20
    print(f"{'Row':>4} {'Actual':>7} {'Old%':>7} {'OldLvl':>8} {'New%':>7} {'NewLvl':>8} {'Δ':>7}")
    print("-" * 55)
    for i in range(min(20, len(X_all))):
        old_pct = round(old_probs_all[i] * 100, 1)
        new_pct = round(new_probs_all[i] * 100, 1)
        delta = round(new_pct - old_pct, 1)
        actual = int(y_all.iloc[i])
        old_lvl = get_risk_level_old(old_pct)
        new_lvl = get_risk_level_new(new_pct)
        print(f"{i+1:>4} {actual:>7} {old_pct:>6}% {old_lvl:>8} {new_pct:>6}% {new_lvl:>8} {delta:>+6}%")

    # --- Aggregate stats ---
    print("\n" + "=" * 75)
    print("AGGREGATE STATISTICS (all rows)")
    print("=" * 75)

    old_pcts = old_probs_all * 100
    new_pcts = new_probs_all * 100
    diffs = new_pcts - old_pcts

    print(f"Mean old risk score:  {old_pcts.mean():.1f}%")
    print(f"Mean new risk score:  {new_pcts.mean():.1f}%")
    print(f"Mean Δ:               {diffs.mean():+.1f}%")
    print(f"Std Δ:                {diffs.std():.1f}%")
    print(f"Max Δ:                {diffs.max():+.1f}%")
    print(f"Min Δ:                {diffs.min():+.1f}%")
    print(f"Correlation:          {np.corrcoef(old_pcts, new_pcts)[0,1]:.4f}")

    # Accuracy comparison — flip target since both models treat 1=disease
    # but the CSV has 1=healthy in this Kaggle version
    y_flipped = 1 - y_all.values
    old_pred = (old_probs_all > 0.5).astype(int)
    new_pred = (new_probs_all > 0.5).astype(int)
    print(f"\nOld model accuracy (on full CSV, flipped): {(old_pred == y_flipped).mean():.4f}")
    print(f"New model accuracy (on full CSV, flipped): {(new_pred == y_flipped).mean():.4f}")

    print("\n[OK] Comparison complete!")


if __name__ == "__main__":
    compare()
