import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.user_model import UserModel


@pytest.mark.asyncio
async def test_login_for_access_token(async_client, test_user: UserModel):
    response = await async_client.post("/auth/login", data={"username": "testuser", "password": "password"})
    assert response.status_code == 200
    json_response = response.json()
    assert "access_token" in json_response
    assert json_response["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_for_access_token_user_not_found(async_client, db_session: AsyncSession):
    response = await async_client.post("/auth/login", data={"username": "nonexistentuser", "password": "password"})
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found."}

@pytest.mark.asyncio
async def test_login_for_access_token_wrong_password(async_client, test_user: UserModel):
    response = await async_client.post("/auth/login", data={"username": "testuser", "password": "wrongpassword"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect password."}


@pytest.mark.asyncio
async def test_refresh_token(async_client, test_user: UserModel):
    login_response = await async_client.post("/auth/login", data={"username": "testuser", "password": "password"})
    assert login_response.status_code == 200
    login_json = login_response.json()
    assert "refresh_token" in login_json
    refresh_token = login_json["refresh_token"]

    refresh_response = await async_client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_response.status_code == 200
    refresh_json = refresh_response.json()
    assert "access_token" in refresh_json
    assert refresh_json["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_refresh_token_invalid(async_client):
    response = await async_client.post("/auth/refresh", json={"refresh_token": "invalidtoken"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials."}


@pytest.mark.asyncio
async def test_logout(async_client, test_user: UserModel, db_session: AsyncSession):
    login_response = await async_client.post("/auth/login", data={"username": "testuser", "password": "password"})
    assert login_response.status_code == 200
    login_json = login_response.json()
    access_token = login_json["access_token"]
    refresh_token = login_json["refresh_token"]

    headers = {"Authorization": f"Bearer {access_token}"}
    logout_response = await async_client.post("/auth/logout", headers=headers, json={"refresh_token": refresh_token})
    assert logout_response.status_code == 200
    assert logout_response.json() == {"detail": "Successfully logged out"}

    refresh_response = await async_client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_response.status_code == 401
    assert refresh_response.json() == {"detail": "Invalid or expired refresh token."}

    # Verify that the access token is also invalidated
    me_response = await async_client.get("/user/me", headers=headers)
    assert me_response.status_code == 401
    assert me_response.json() == {"detail": "Could not validate credentials."}