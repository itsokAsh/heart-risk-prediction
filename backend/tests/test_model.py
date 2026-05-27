from ml.model import load_model, predict


def test_model_predict_range():
    load_model()
    payload = {
        "age": 45,
        "sex": 1,
        "cp": 2,
        "trestbps": 130,
        "chol": 230,
        "fbs": 0,
        "restecg": 0,
        "thalach": 150,
        "exang": 0,
        "oldpeak": 1.0,
        "slope": 1,
        "ca": 0,
        "thal": 1,
    }

    risk_score, risk_level = predict(payload)
    assert 0 <= risk_score <= 100
    assert risk_level in {"Low", "Moderate", "High"}
