import pytest
from pytest_schema import exact_schema
from httpx import AsyncClient
from .schemas import users


@pytest.mark.asyncio
async def test_read_users_unauthorized(client: AsyncClient):
    """
    Testing users path access unauthorized
    """
    response = await client.get("/api/users")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_read_users(client: AsyncClient, create_user, authorization_header):
    """
    Testing users path access authorized
    """
    response = await client.get("/api/users", headers=authorization_header)
    assert response.status_code == 200
    assert response.json() != []
    assert exact_schema(users) == response.json()
