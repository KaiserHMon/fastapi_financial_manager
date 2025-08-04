import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from main import app
from models.user_model import UserModel
from models.incomes_model import IncomeModel
from models.categories_model import CategoryModel
from models.expenses_model import ExpenseModel
from models.history_model import HistoryModel
from dependencies import get_async_db
from services.password_services import get_password_hash


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
async def test_category(db_session: AsyncSession, test_user: UserModel):
    category = CategoryModel(
        name="Test Category",
        type="income",
        user_id=test_user.id
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    return category


@pytest.fixture(scope="function")
async def access_token(async_client: AsyncClient, test_user: UserModel):
    response = await async_client.post("/auth/login", data={"username": "testuser", "password": "password"})
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_create_income(async_client: AsyncClient, access_token: str, test_user: UserModel, test_category: CategoryModel):
    response = await async_client.post("/incomes/", headers={"Authorization": f"Bearer {access_token}"}, json={"amount": 100, "description": "Test Income", "date": "2025-07-21T14:00:00", "category_id": test_category.id})
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 100
    assert data["description"] == "Test Income"
    assert data["user_id"] == test_user.id
    assert data["category_id"] == test_category.id

@pytest.mark.asyncio
async def test_get_incomes(async_client: AsyncClient, access_token: str, test_user: UserModel, test_category: CategoryModel):
    response = await async_client.post("/incomes/", headers={"Authorization": f"Bearer {access_token}"}, json={"amount": 100, "description": "Test Income", "date": "2025-07-21T14:00:00", "category_id": test_category.id})
    assert response.status_code == 200

    response = await async_client.get("/incomes/", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["amount"] == 100
    assert data[0]["description"] == "Test Income"
    assert data[0]["user_id"] == test_user.id
    assert data[0]["category_id"] == test_category.id


@pytest.mark.asyncio
async def test_get_income_by_id(async_client: AsyncClient, access_token: str, test_user: UserModel, test_category: CategoryModel):
    response = await async_client.post("/incomes/", headers={"Authorization": f"Bearer {access_token}"}, json={"amount": 100, "description": "Test Income", "date": "2025-07-21T14:00:00", "category_id": test_category.id})
    assert response.status_code == 200
    income_id = response.json()["id"]

    response = await async_client.get(f"/incomes/{income_id}", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 100
    assert data["description"] == "Test Income"
    assert data["user_id"] == test_user.id
    assert data["category_id"] == test_category.id


@pytest.mark.asyncio
async def test_update_income(async_client: AsyncClient, access_token: str, test_user: UserModel, test_category: CategoryModel):
    response = await async_client.post("/incomes/", headers={"Authorization": f"Bearer {access_token}"}, json={"amount": 100, "description": "Test Income", "date": "2025-07-21T14:00:00", "category_id": test_category.id})
    assert response.status_code == 200
    income_id = response.json()["id"]

    response = await async_client.put(f"/incomes/{income_id}", headers={"Authorization": f"Bearer {access_token}"}, json={"amount": 200, "description": "Updated Income", "date": "2025-07-21T14:00:00", "category_id": test_category.id})
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 200
    assert data["description"] == "Updated Income"


@pytest.mark.asyncio
async def test_delete_income(async_client: AsyncClient, access_token: str, test_user: UserModel, test_category: CategoryModel):
    response = await async_client.post("/incomes/", headers={"Authorization": f"Bearer {access_token}"}, json={"amount": 100, "description": "Test Income", "date": "2025-07-21T14:00:00", "category_id": test_category.id})
    assert response.status_code == 200
    income_id = response.json()["id"]

    response = await async_client.delete(f"/incomes/{income_id}", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200

    response = await async_client.get(f"/incomes/{income_id}", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 404
