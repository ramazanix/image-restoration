import pytest
from pytest_schema import exact_schema
from httpx import AsyncClient
from .schemas import users


@pytest.mark.asyncio
async def test_base_url(client: AsyncClient):
    """
    Testing users path access
    """
    response = await client.get("/api/users")
    assert response.status_code == 200
    assert response.json() == []
    print(users)
    assert exact_schema(users) == response.json()
