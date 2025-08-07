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
        name="Test Category",
        type="income",
        user_id=test_user.id
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    return category


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
