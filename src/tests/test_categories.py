import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.user_model import UserModel
from ..services.password_services import PasswordService


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


@pytest.mark.asyncio
async def test_create_category(async_client: AsyncClient, access_token: str, test_user: UserModel):
    response = await async_client.post("/categories/", headers={"Authorization": f"Bearer {access_token}"}, json={"name": "Test Category", "type": "expense"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Category"
    assert data["type"] == "expense"
    assert data["user_id"] == test_user.id

@pytest.mark.asyncio
async def test_get_categories(async_client: AsyncClient, access_token: str, test_user: UserModel):
    response = await async_client.post("/categories/", headers={"Authorization": f"Bearer {access_token}"}, json={"name": "Test Category 1", "type": "expense"})
    assert response.status_code == 201
    response = await async_client.post("/categories/", headers={"Authorization": f"Bearer {access_token}"}, json={"name": "Test Category 2", "type": "income"})
    assert response.status_code == 201

    response = await async_client.get("/categories/", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Test Category 1"
    assert data[1]["name"] == "Test Category 2"


@pytest.mark.asyncio
async def test_get_category_by_id(async_client: AsyncClient, access_token: str, test_user: UserModel):
    response = await async_client.post("/categories/", headers={"Authorization": f"Bearer {access_token}"}, json={"name": "Test Category", "type": "expense"})
    assert response.status_code == 201
    category_id = response.json()["id"]

    response = await async_client.get(f"/categories/{category_id}", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Category"
    assert data["type"] == "expense"
    assert data["user_id"] == test_user.id


@pytest.mark.asyncio
async def test_update_category(async_client: AsyncClient, access_token: str, test_user: UserModel):
    response = await async_client.post("/categories/", headers={"Authorization": f"Bearer {access_token}"}, json={"name": "Test Category", "type": "expense"})
    assert response.status_code == 201
    category_id = response.json()["id"]

    response = await async_client.put(f"/categories/{category_id}", headers={"Authorization": f"Bearer {access_token}"}, json={"name": "Updated Category", "type": "income"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Category"
    assert data["type"] == "income"


@pytest.mark.asyncio
async def test_delete_category(async_client: AsyncClient, access_token: str, test_user: UserModel):
    response = await async_client.post("/categories/", headers={"Authorization": f"Bearer {access_token}"}, json={"name": "Test Category", "type": "expense"})
    assert response.status_code == 201
    category_id = response.json()["id"]

    response = await async_client.delete(f"/categories/{category_id}", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 204

    response = await async_client.get(f"/categories/{category_id}", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 404