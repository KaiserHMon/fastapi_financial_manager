import os
import pytest
from fastapi import Depends

from httpx import AsyncClient, ASGITransport
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from main import app
from models.user_model import UserModel
from dependencies import get_async_db
from services.password_services import get_password_hash



DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)



@pytest.fixture(scope="function")
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(UserModel.metadata.create_all)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        await db.close()
        async with engine.begin() as conn:
            await conn.run_sync(UserModel.metadata.drop_all)

@pytest.fixture(scope="function")
async def test_user(db_session: AsyncSession):
    user = UserModel(
        username="testuser",
        full_name="Test User",
        email="testuser@example.com",
        password=get_password_hash("password"),
    )
    db_session.add(user)
    await db_session.commit()
    return user

@pytest.fixture(scope="function")
async def async_client(db_session: AsyncSession):
    async def get_test_db():
        yield db_session
    app.dependency_overrides[get_async_db] = get_test_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear() # Clear overrides after test



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

    refresh_response = await async_client.post("/auth/refresh", headers={"Authorization": f"Bearer {refresh_token}"})
    assert refresh_response.status_code == 200
    refresh_json = refresh_response.json()
    assert "access_token" in refresh_json
    assert refresh_json["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_refresh_token_invalid(async_client):
    response = await async_client.post("/auth/refresh", headers={"Authorization": "Bearer invalidtoken"})
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

    refresh_response = await async_client.post("/auth/refresh", headers={"Authorization": f"Bearer {refresh_token}"})
    assert refresh_response.status_code == 401
    assert refresh_response.json() == {"detail": "Invalid or expired refresh token."}