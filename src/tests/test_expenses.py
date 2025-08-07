import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.user_model import UserModel
from ..models.categories_model import CategoryModel
from ..services.password_services import get_password_hash


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
        name="Test Expense Category",
        type="expense",
        user_id=test_user.id
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    return category


@pytest.mark.asyncio
async def test_create_expense(async_client: AsyncClient, access_token: str, test_user: UserModel, test_category: CategoryModel):
    response = await async_client.post("/expenses/", headers={"Authorization": f"Bearer {access_token}"}, json={"amount": 50, "description": "Test Expense", "date": "2025-07-21T14:00:00", "category_id": test_category.id})
    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == 50
    assert data["description"] == "Test Expense"
    assert data["user_id"] == test_user.id
    assert data["category_id"] == test_category.id

@pytest.mark.asyncio
async def test_get_expenses(async_client: AsyncClient, access_token: str, test_user: UserModel, test_category: CategoryModel):
    response = await async_client.post("/expenses/", headers={"Authorization": f"Bearer {access_token}"}, json={"amount": 50, "description": "Test Expense", "date": "2025-07-21T14:00:00", "category_id": test_category.id})
    assert response.status_code == 201

    response = await async_client.get("/expenses/", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["amount"] == 50
    assert data[0]["description"] == "Test Expense"
    assert data[0]["user_id"] == test_user.id
    assert data[0]["category_id"] == test_category.id


@pytest.mark.asyncio
async def test_get_expense_by_id(async_client: AsyncClient, access_token: str, test_user: UserModel, test_category: CategoryModel):
    response = await async_client.post("/expenses/", headers={"Authorization": f"Bearer {access_token}"}, json={"amount": 50, "description": "Test Expense", "date": "2025-07-21T14:00:00", "category_id": test_category.id})
    assert response.status_code == 201
    expense_id = response.json()["id"]

    response = await async_client.get(f"/expenses/{expense_id}", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 50
    assert data["description"] == "Test Expense"
    assert data["user_id"] == test_user.id
    assert data["category_id"] == test_category.id


@pytest.mark.asyncio
async def test_update_expense(async_client: AsyncClient, access_token: str, test_user: UserModel, test_category: CategoryModel):
    response = await async_client.post("/expenses/", headers={"Authorization": f"Bearer {access_token}"}, json={"amount": 50, "description": "Test Expense", "date": "2025-07-21T14:00:00", "category_id": test_category.id})
    assert response.status_code == 201
    expense_id = response.json()["id"]

    response = await async_client.put(f"/expenses/{expense_id}", headers={"Authorization": f"Bearer {access_token}"}, json={"amount": 75, "description": "Updated Expense", "date": "2025-07-21T14:00:00", "category_id": test_category.id})
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 75
    assert data["description"] == "Updated Expense"


@pytest.mark.asyncio
async def test_delete_expense(async_client: AsyncClient, access_token: str, test_user: UserModel, test_category: CategoryModel):
    response = await async_client.post("/expenses/", headers={"Authorization": f"Bearer {access_token}"}, json={"amount": 50, "description": "Test Expense", "date": "2025-07-21T14:00:00", "category_id": test_category.id})
    assert response.status_code == 201
    expense_id = response.json()["id"]

    response = await async_client.delete(f"/expenses/{expense_id}", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 204

    response = await async_client.get(f"/expenses/{expense_id}", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 404