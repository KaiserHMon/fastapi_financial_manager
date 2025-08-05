import os
import pytest
from fastapi import Depends

from httpx import AsyncClient, ASGITransport
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from ..main import app
from ..models.user_model import UserModel
from ..dependencies import get_async_db
from ..services.user_services import get_user, get_user_by_email, create_user, update_user
from ..services.password_services import get_password_hash
from ..schemas.user_schema import UserIn, UserBase


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
async def async_client(db_session: AsyncSession):
    async def get_test_db():
        yield db_session
    app.dependency_overrides[get_async_db] = get_test_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear() # Clear overrides after test


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
    await db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
async def access_token(async_client: AsyncClient, test_user: UserModel):
    response = await async_client.post("/auth/login", data={"username": "testuser", "password": "password"})
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_get_user(db_session: AsyncSession):
    user = await get_user(db_session, "testuser")
    assert user is None


@pytest.mark.asyncio
async def test_get_user_by_email(db_session: AsyncSession):
    user = await get_user_by_email(db_session, "test@example.com")
    assert user is None


@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    user_in = UserIn(username="testuser", full_name="Test User", email="test@example.com", password="password")
    user = await create_user(db_session, user_in)
    assert user.username == "testuser"
    assert user.full_name == "Test User"
    assert user.email == "test@example.com"


@pytest.mark.asyncio
async def test_update_user(db_session: AsyncSession):
    user_in = UserIn(username="testuser", full_name="Test User", email="test@example.com", password="password")
    user = await create_user(db_session, user_in)
    user_update = UserBase(username="testuser2", full_name="Test User 2", email="test2@example.com")
    updated_user = await update_user(db_session, user, user_update)
    assert updated_user.username == "testuser2"
    assert updated_user.full_name == "Test User 2"
    assert updated_user.email == "test2@example.com"
    
    
@pytest.mark.asyncio
async def test_register_user(async_client: AsyncClient):
    response = await async_client.post("/user/register", json={"username": "testuser", "full_name": "Test User", "email": "test@example.com", "password": "password"})
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["full_name"] == "Test User"
    assert data["email"] == "test@example.com"
    assert "password" not in data


@pytest.mark.asyncio
async def test_register_user_already_exists(async_client: AsyncClient, db_session: AsyncSession):
    user_in = UserIn(username="testuser", full_name="Test User", email="test@example.com", password="password")
    await create_user(db_session, user_in)
    response = await async_client.post("/user/register", json={"username": "testuser", "full_name": "Test User", "email": "test2@example.com", "password": "password"})
    assert response.status_code == 409
    assert response.json()["detail"] == "Username already registered. Use a different username."


@pytest.mark.asyncio
async def test_register_user_email_already_exists(async_client: AsyncClient, db_session: AsyncSession):
    user_in = UserIn(username="testuser", full_name="Test User", email="test@example.com", password="password")
    await create_user(db_session, user_in)
    response = await async_client.post("/user/register", json={"username": "testuser2", "full_name": "Test User 2", "email": "test@example.com", "password": "password"})
    assert response.status_code == 422
    assert response.json()["detail"] == "Email already registered. Use a different email."


@pytest.mark.asyncio
async def test_get_current_user(async_client: AsyncClient, access_token: str):
    response = await async_client.get("/user/me", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["full_name"] == "Test User"
    assert data["email"] == "testuser@example.com"


@pytest.mark.asyncio
async def test_update_current_user(async_client: AsyncClient, access_token: str):
    response = await async_client.put("/user/me", headers={"Authorization": f"Bearer {access_token}"}, json={"username": "testuser2", "full_name": "Test User 2", "email": "test2@example.com"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser2"
    assert data["full_name"] == "Test User 2"
    assert data["email"] == "test2@example.com"


@pytest.mark.asyncio
async def test_delete_current_user(async_client: AsyncClient, access_token: str, db_session: AsyncSession):
    response = await async_client.delete("/user/me", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 204
    user = await get_user(db_session, "testuser")
    assert user is None


@pytest.mark.asyncio
async def test_get_current_user_no_token(async_client: AsyncClient):
    response = await async_client.get("/user/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_update_current_user_no_token(async_client: AsyncClient):
    response = await async_client.put("/user/me", json={"username": "testuser2", "full_name": "Test User 2", "email": "test2@example.com"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_delete_current_user_no_token(async_client: AsyncClient):
    response = await async_client.delete("/user/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(async_client: AsyncClient):
    response = await async_client.get("/user/me", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials."


@pytest.mark.asyncio
async def test_update_current_user_invalid_token(async_client: AsyncClient):
    response = await async_client.put("/user/me", headers={"Authorization": "Bearer invalidtoken"}, json={"username": "testuser2", "full_name": "Test User 2", "email": "test2@example.com"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials."


@pytest.mark.asyncio
async def test_delete_current_user_invalid_token(async_client: AsyncClient):
    response = await async_client.delete("/user/me", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials."
