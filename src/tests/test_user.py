import pytest

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from ..services.user_services import get_user, get_user_by_email, create_user, update_user
from ..schemas.user_schema import UserIn, UserUpdateProfile


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
    user_update = UserUpdateProfile(full_name="Updated User") 
    updated_user = await update_user(db_session, user, user_update)
    assert updated_user.username == "testuser"
    assert updated_user.full_name == "Updated User"
    assert updated_user.email == "test@example.com"
    
    
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
    response = await async_client.put("/user/me", 
                                      headers={"Authorization": f"Bearer {access_token}"}, 
                                      json={"full_name": "Test User 2"}) 
    data = response.json()
    assert data["username"] == "testuser"
    assert data["full_name"] == "Test User 2"
    assert data["email"] == "testuser@example.com"


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


@pytest.mark.asyncio
async def test_get_user_by_id(async_client: AsyncClient, access_token: str, db_session: AsyncSession):
    user_in = UserIn(username="testuser2", full_name="Test User 2", email="test2@example.com", password="password")
    user = await create_user(db_session, user_in)
    response = await async_client.get(f"/user/{user.id}", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser2"
    assert data["full_name"] == "Test User 2"
    assert data["email"] == "test2@example.com"


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(async_client: AsyncClient, access_token: str):
    response = await async_client.get("/user/999", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found."


@pytest.mark.asyncio
async def test_get_user_history(async_client: AsyncClient, access_token: str):
    response = await async_client.get("/user/me/history", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_user_history_with_dates(async_client: AsyncClient, access_token: str):
    response = await async_client.get("/user/me/history?from_date=2023-01-01&to_date=2023-12-31", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_user_history_with_pagination(async_client: AsyncClient, access_token: str):
    response = await async_client.get("/user/me/history?skip=0&limit=10", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_change_password(async_client: AsyncClient, access_token: str):
    response = await async_client.put("/user/me/password",
                                      headers={"Authorization": f"Bearer {access_token}"},
                                      json={"old_password": "password", "new_password": "new_password"})
    assert response.status_code == 200
    assert response.json()["detail"] == "Password updated successfully"

    # Try to log in with the new password
    response = await async_client.post("/auth/login", data={"username": "testuser", "password": "new_password"})
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_change_password_invalid_old_password(async_client: AsyncClient, access_token: str):
    response = await async_client.put("/user/me/password",
                                      headers={"Authorization": f"Bearer {access_token}"},
                                      json={"old_password": "wrong_password", "new_password": "new_password"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid old password"


@pytest.mark.asyncio
async def test_change_password_no_token(async_client: AsyncClient):
    response = await async_client.put("/user/me/password",
                                      json={"old_password": "password", "new_password": "new_password"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_change_password_invalid_token(async_client: AsyncClient):
    response = await async_client.put("/user/me/password",
                                      headers={"Authorization": "Bearer invalidtoken"},
                                      json={"old_password": "password", "new_password": "new_password"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials."