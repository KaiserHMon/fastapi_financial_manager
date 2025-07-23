import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from main import app
from models.user_model import UserModel
from models.incomes_model import IncomeModel
from dependencies import get_async_db
from services.password_services import get_password_hash
from schemas.incomes_schema import IncomeIn


DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)


@pytest.fixture(scope="function")
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(UserModel.metadata.create_all)
        await conn.run_sync(IncomeModel.metadata.create_all)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        await db.close()
        async with engine.begin() as conn:
            await conn.run_sync(IncomeModel.metadata.drop_all)
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
    response = await async_client.post("/login", data={"username": "testuser", "password": "password"})
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_create_income(async_client: AsyncClient, access_token: str, test_user: UserModel):
    response = await async_client.post("/incomes", headers={"Authorization": f"Bearer {access_token}"}, json={"amount": 100, "description": "Test Income", "date": "2025-07-21T14:00:00"})
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 100
    assert data["description"] == "Test Income"
    assert data["user_id"] == test_user.id
