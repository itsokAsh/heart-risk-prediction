import pytest


async def _register_and_login(async_client, email: str) -> str:
    register_payload = {
        "email": email,
        "password": "StrongPass123",
        "full_name": "Predict User",
    }
    register_response = await async_client.post("/api/auth/register", json=register_payload)
    assert register_response.status_code == 201
    return register_response.json()["access_token"]


@pytest.mark.asyncio
async def test_predict_requires_auth(async_client):
    response = await async_client.post("/api/predict", json={})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_predict_valid_payload(async_client, unique_email):
    token = await _register_and_login(async_client, unique_email)

    payload = {
        "age": 58,
        "sex": 1,
        "cp": 1,
        "trestbps": 144,
        "chol": 256,
        "fbs": 1,
        "restecg": 1,
        "thalach": 115,
        "exang": 1,
        "oldpeak": 1.5,
        "slope": 1,
        "ca": 1,
        "thal": 1,
    }

    response = await async_client.post(
        "/api/predict",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["risk_score"] >= 0
    assert body["risk_score"] <= 100
    assert body["risk_level"] in {"Low", "Moderate", "High"}
    assert body["id"]


@pytest.mark.asyncio
async def test_predict_invalid_payload(async_client, unique_email):
    token = await _register_and_login(async_client, unique_email)

    payload = {
        "age": 10,
        "sex": 1,
        "cp": 1,
        "trestbps": 144,
        "chol": 256,
        "fbs": 1,
        "restecg": 1,
        "thalach": 115,
        "exang": 1,
        "oldpeak": 1.5,
        "slope": 1,
        "ca": 1,
        "thal": 1,
    }

    response = await async_client.post(
        "/api/predict",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422
