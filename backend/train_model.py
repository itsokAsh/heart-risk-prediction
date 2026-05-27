"""
Heart Disease Risk Prediction — Model Training Pipeline
========================================================
Uses the UCI Cleveland heart disease dataset (303 rows, 14 features).
Trains an XGBoost classifier with RandomizedSearchCV hyperparameter tuning,
then wraps it in CalibratedClassifierCV for well-calibrated probabilities.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import randint, uniform
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.model_selection import (
    RandomizedSearchCV,
    StratifiedKFold,
    train_test_split,
)
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
import pickle
import warnings

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "heart.csv"
ARTIFACTS_DIR = BASE_DIR / "ml" / "artifacts"


def load_and_preprocess_data():
    """
    Load the UCI Cleveland heart disease dataset, clean it, and split.

    Cleaning steps:
    - Drop exact duplicate rows
    - Replace sentinel values: ca=4 -> NaN (then mode-impute), thal=0 -> NaN (then mode-impute)
    """
    df = pd.read_csv(DATA_PATH)
    print(f"Raw dataset: {df.shape[0]} rows, {df.shape[1]} columns")

    # --- Deduplication ---
    n_before = len(df)
    df = df.drop_duplicates()
    n_dropped = n_before - len(df)
    if n_dropped:
        print(f"Dropped {n_dropped} duplicate rows -> {len(df)} remaining")

    # --- Handle sentinel / impossible values ---
    # ca should be 0-3; value 4 is a known data entry sentinel
    if (df["ca"] == 4).any():
        n_bad = (df["ca"] == 4).sum()
        df.loc[df["ca"] == 4, "ca"] = np.nan
        df["ca"] = df["ca"].fillna(df["ca"].mode()[0])
        print(f"Fixed {n_bad} rows with ca=4 (sentinel -> mode-imputed)")

    # thal should be 1-3; value 0 is a sentinel
    if (df["thal"] == 0).any():
        n_bad = (df["thal"] == 0).sum()
        df.loc[df["thal"] == 0, "thal"] = np.nan
        df["thal"] = df["thal"].fillna(df["thal"].mode()[0])
        print(f"Fixed {n_bad} rows with thal=0 (sentinel -> mode-imputed)")

    print(f"\nFinal dataset: {len(df)} rows")
    print(f"Target distribution:\n{df['target'].value_counts().to_string()}")
    print()

    # --- Split features / target ---
    X = df.drop("target", axis=1)
    y = df["target"]

    # IMPORTANT: In this Kaggle version of the UCI Cleveland dataset,
    # target=1 means "healthy" and target=0 means "disease present."
    # Our app expects target=1 = disease (high risk), so we flip it.
    y = 1 - y
    print(f"Target flipped (1=disease, 0=healthy):")
    print(f"  Disease: {y.sum()}, Healthy: {(1 - y).sum()}")

    # Stratified train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    return X_train_scaled, X_test_scaled, y_train, y_test, scaler, X.columns.tolist()


def train_model():
    """Train an XGBoost model with hyperparameter search and calibration."""
    X_train, X_test, y_train, y_test, scaler, feature_names = load_and_preprocess_data()

    print("=" * 60)
    print("STEP 1: Hyperparameter Search (RandomizedSearchCV)")
    print("=" * 60)

    # Define search space
    param_distributions = {
        "n_estimators": randint(100, 500),
        "learning_rate": uniform(0.01, 0.19),       # 0.01 – 0.20
        "max_depth": randint(3, 8),                  # 3 – 7
        "min_child_weight": randint(1, 6),           # 1 – 5
        "gamma": uniform(0, 0.5),
        "subsample": uniform(0.6, 0.4),              # 0.6 – 1.0
        "colsample_bytree": uniform(0.6, 0.4),       # 0.6 – 1.0
        "reg_alpha": uniform(0, 1.0),
        "reg_lambda": uniform(0.5, 1.5),             # 0.5 – 2.0
    }

    base_xgb = XGBClassifier(
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=42,
    )

    cv_strategy = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    search = RandomizedSearchCV(
        estimator=base_xgb,
        param_distributions=param_distributions,
        n_iter=80,
        scoring="roc_auc",
        cv=cv_strategy,
        random_state=42,
        n_jobs=-1,
        verbose=0,
    )

    search.fit(X_train, y_train)

    print(f"\nBest CV ROC-AUC: {search.best_score_:.4f}")
    print(f"Best parameters:")
    for k, v in search.best_params_.items():
        print(f"  {k}: {v:.4f}" if isinstance(v, float) else f"  {k}: {v}")

    # -----------------------------------------------------------------
    print("\n" + "=" * 60)
    print("STEP 2: Probability Calibration (Isotonic)")
    print("=" * 60)

    # Wrap the best estimator in isotonic calibration
    calibrated_model = CalibratedClassifierCV(
        search.best_estimator_,
        cv=5,
        method="isotonic",
    )
    calibrated_model.fit(X_train, y_train)

    # -----------------------------------------------------------------
    print("\n" + "=" * 60)
    print("STEP 3: Evaluation on Hold-out Test Set")
    print("=" * 60)

    y_pred = calibrated_model.predict(X_test)
    y_prob = calibrated_model.predict_proba(X_test)[:, 1]

    accuracy = accuracy_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_prob)
    brier = brier_score_loss(y_test, y_prob)

    print(f"\nAccuracy:    {accuracy:.4f}")
    print(f"ROC-AUC:     {roc_auc:.4f}")
    print(f"Brier Score: {brier:.4f}  (lower is better)")
    print(f"\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(f"  TN={cm[0][0]}  FP={cm[0][1]}")
    print(f"  FN={cm[1][0]}  TP={cm[1][1]}")
    print(f"\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["No Disease", "Disease"]))

    # -----------------------------------------------------------------
    print("=" * 60)
    print("STEP 4: Saving Artifacts")
    print("=" * 60)

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(ARTIFACTS_DIR / "xgb_model.pkl", "wb") as f:
        pickle.dump(calibrated_model, f)
    with open(ARTIFACTS_DIR / "scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)

    print(f"  -> Model saved to {ARTIFACTS_DIR / 'xgb_model.pkl'}")
    print(f"  -> Scaler saved to {ARTIFACTS_DIR / 'scaler.pkl'}")

    # -----------------------------------------------------------------
    print("\n" + "=" * 60)
    print("STEP 5: Test Case Predictions")
    print("=" * 60)

    test_cases = [
        {
            "name": "High Risk Case",
            "data": {
                "age": 58, "sex": 1, "cp": 1, "trestbps": 144,
                "chol": 256, "fbs": 1, "restecg": 1, "thalach": 115,
                "exang": 1, "oldpeak": 1.5, "slope": 1, "ca": 1, "thal": 3,
            },
        },
        {
            "name": "Low Risk Case",
            "data": {
                "age": 32, "sex": 0, "cp": 0, "trestbps": 115,
                "chol": 170, "fbs": 0, "restecg": 0, "thalach": 165,
                "exang": 0, "oldpeak": 0.1, "slope": 0, "ca": 0, "thal": 1,
            },
        },
        {
            "name": "Moderate Risk Case",
            "data": {
                "age": 52, "sex": 1, "cp": 2, "trestbps": 130,
                "chol": 230, "fbs": 0, "restecg": 1, "thalach": 155,
                "exang": 0, "oldpeak": 0.8, "slope": 2, "ca": 0, "thal": 2,
            },
        },
    ]

    for case in test_cases:
        test_df = pd.DataFrame([case["data"]])
        test_scaled = scaler.transform(test_df)
        prob = calibrated_model.predict_proba(test_scaled)[0][1]
        risk_pct = round(prob * 100, 2)

        if risk_pct > 60:
            level = "High"
        elif risk_pct > 30:
            level = "Moderate"
        else:
            level = "Low"

        print(f"\n{case['name']}:")
        print(f"  Risk Score:  {risk_pct}%")
        print(f"  Risk Level:  {level}")

    print("\n[OK] Training complete!")
    return calibrated_model, scaler


if __name__ == "__main__":
    train_model()
