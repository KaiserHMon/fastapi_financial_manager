import pytest
from httpx import AsyncClient, ASGITransport

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.backends.inmemory import InMemoryBackend
from redis import asyncio as aioredis
import redis

from ..main import app
from ..models.user_model import UserModel
from ..models.incomes_model import IncomeModel
from ..models.categories_model import CategoryModel
from ..models.expenses_model import ExpenseModel
from ..models.history_model import HistoryModel
from ..dependencies import get_async_db
from ..services.password_services import PasswordService
from ..config.settings import settings


DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="function", autouse=True)
async def initialize_cache():
    try:
        if settings.REDIS_URL:
            redis_client = aioredis.from_url(settings.REDIS_URL, encoding="utf8", decode_responses=True)
            await redis_client.ping()
            FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")
        else:
            FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
    except (redis.exceptions.ConnectionError, ValueError):
        FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
    yield
    await FastAPICache.clear()


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
async def async_client(db_session: AsyncSession, initialize_cache):
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
        password=PasswordService.hash_password("password"),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
async def access_token(async_client: AsyncClient, test_user: UserModel):
    response = await async_client.post("/auth/login", data={"username": "testuser", "password": "password"})
    return response.json()["access_token"]
