import pytest


@pytest.mark.asyncio
async def test_register_and_login(async_client, unique_email):
    register_payload = {
        "email": unique_email,
        "password": "StrongPass123",
        "full_name": "Test User",
    }

    register_response = await async_client.post("/api/auth/register", json=register_payload)
    assert register_response.status_code == 201
    register_body = register_response.json()
    assert "access_token" in register_body
    assert register_body["user"]["email"] == unique_email

    login_payload = {
        "email": unique_email,
        "password": "StrongPass123",
    }

    login_response = await async_client.post("/api/auth/login", json=login_payload)
    assert login_response.status_code == 200
    login_body = login_response.json()
    assert "access_token" in login_body
    assert login_body["user"]["email"] == unique_email


@pytest.mark.asyncio
async def test_login_invalid_credentials(async_client, unique_email):
    login_payload = {
        "email": unique_email,
        "password": "WrongPass123",
    }

    login_response = await async_client.post("/api/auth/login", json=login_payload)
    assert login_response.status_code == 401
