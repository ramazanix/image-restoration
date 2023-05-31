import pytest
from httpx import AsyncClient
from pytest_schema import exact_schema
from .schemas import user


user_data = {"username": "username", "password": "password"}


@pytest.mark.asyncio
async def test_update_user_unauthorized(client: AsyncClient, create_user):
    """
    Trying to update user without auth
    """
    response = await client.patch(
        f"/api/users/{user_data['username']}", json={"username": "not_User"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_user_authorized(
    client: AsyncClient, create_user, authorization_header
):
    """
    Trying to update user with auth
    """
    response = await client.patch(
        "/api/users/username",
        json={"username": "not_User"},
        headers=authorization_header,
    )
    assert response.status_code == 200
    assert exact_schema(user) == response.json()
    assert response.json().get("username") == "not_User"

    response = await client.get(
        f"/api/users/{user_data['username']}", headers=authorization_header
    )
    assert response.status_code == 400
    assert response.json().get("detail") == "User not found"

    response = await client.get("/api/users/not_User", headers=authorization_header)
    assert response.status_code == 200
    assert exact_schema(user) == response.json()
    assert response.json().get("username") == "not_User"


@pytest.mark.asyncio
async def test_update_another_user(
    client: AsyncClient, create_user, authorization_header
):
    """
    Trying to update another user
    """
    response = await client.post(
        "/api/users", json={"username": "user2", "password": "password"}
    )
    assert response.status_code == 201
    assert exact_schema(user) == response.json()
    assert response.json().get("username") == "user2"

    response = await client.patch(
        "/api/users/user2", json={"password": "12345678"}, headers=authorization_header
    )
    assert response.status_code == 405
    assert response.json().get("detail") == "Method Not Allowed"


@pytest.mark.asyncio
async def test_update_user_blank_body(
    client: AsyncClient, create_user, authorization_header
):
    """
    Trying to update user with blank body
    """
    response = await client.patch(
        f"/api/users/{user_data['username']}", json={}, headers=authorization_header
    )
    assert response.status_code == 400
    assert response.json().get("detail") == "Bad Request"


@pytest.mark.asyncio
async def test_update_user_too_small_username(
    client: AsyncClient, create_user, authorization_header
):
    """
    Trying to update user's username to small value
    """
    response = await client.patch(
        "/api/users/username", json={"username": "J"}, headers=authorization_header
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_user_too_long_username(
    client: AsyncClient, create_user, authorization_header
):
    """
    Trying to update user's username to long value
    """
    response = await client.patch(
        "/api/users/username", json={"username": "A" * 21}, headers=authorization_header
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_user_too_small_password(
    client: AsyncClient, create_user, authorization_header
):
    """
    Trying to update user's password to small value
    """
    response = await client.patch(
        "/api/users/username", json={"password": "A" * 33}, headers=authorization_header
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_user_too_long_password(
    client: AsyncClient, create_user, authorization_header
):
    """
    Trying to update user's password to long value
    """
    response = await client.patch(
        "/api/users/username", json={"password": "A" * 33}, headers=authorization_header
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_user_invalid_body(
    client: AsyncClient, create_user, authorization_header
):
    """
    Trying to update user with invalid body keys
    """
    response = await client.patch(
        "/api/users/username", json={"a": "b"}, headers=authorization_header
    )
    assert response.status_code == 400
    assert response.json().get("detail") == "Bad Request"


@pytest.mark.asyncio
async def test_update_user_blank_username(
    client: AsyncClient, create_user, authorization_header
):
    """
    Trying to update user with blank username value
    """
    response = await client.patch(
        "/api/users/username", json={"username": ""}, headers=authorization_header
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_user_blank_password(
    client: AsyncClient, create_user, authorization_header
):
    """
    Trying to update user with blank password value
    """
    response = await client.patch(
        "/api/users/username", json={"password": ""}, headers=authorization_header
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_user_username_blank_password(
    client: AsyncClient, create_user, authorization_header
):
    """
    Trying to update user with filled username value and blank password value
    """
    response = await client.patch(
        "/api/users/username",
        json={"username": "username", "password": ""},
        headers=authorization_header,
    )
    assert response.status_code == 422
