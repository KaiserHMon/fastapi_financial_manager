import pytest
from httpx import AsyncClient

from ..models.user_model import UserModel


@pytest.mark.asyncio
async def test_get_history(
    async_client: AsyncClient, test_user: UserModel, access_token: str
):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await async_client.get("/user/me/history", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
