import pytest
from fastapi import Depends

from httpx import AsyncClient, ASGITransport
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from ..main import app
import uuid
from ..models.user_model import UserModel
from ..models.incomes_model import IncomeModel
from ..models.categories_model import CategoryModel
from ..models.expenses_model import ExpenseModel
from ..models.history_model import HistoryModel
from ..models.token_denylist_model import TokenDenylist
from ..dependencies import get_async_db
from ..services.password_services import get_password_hash
from config.database import base


DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="function")
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(UserModel.metadata.create_all)
        await conn.run_sync(CategoryModel.metadata.create_all)
        await conn.run_sync(IncomeModel.metadata.create_all)
        await conn.run_sync(ExpenseModel.metadata.create_all)
        await conn.run_sync(HistoryModel.metadata.create_all)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        await db.close()
        async with engine.begin() as conn:
            await conn.run_sync(HistoryModel.metadata.drop_all)
            await conn.run_sync(ExpenseModel.metadata.drop_all)
            await conn.run_sync(IncomeModel.metadata.drop_all)
            await conn.run_sync(CategoryModel.metadata.drop_all)
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