import pytest
from pytest_schema import exact_schema
from httpx import AsyncClient
from .schemas import user
from ..auth.schemas import success, error


correct_cookies: list[str] = [
    "access_token_cookie",
    "csrf_access_token",
    "csrf_refresh_token",
    "refresh_token_cookie",
]

user_data = {"username": "Alex", "password": "alex_password"}


@pytest.mark.asyncio
async def test_delete_user_unauthorized(client: AsyncClient):
    """
    Trying to delete user without auth
    """
    response = await client.post("/users", json=user_data)
    assert response.status_code == 201
    assert exact_schema(user) == response.json()
    assert response.json().get("username") == user_data["username"]

    response = await client.delete(f"/users/{user_data['username']}")
    assert response.status_code == 401
    assert exact_schema(error) == response.json()


@pytest.mark.asyncio
async def test_delete_user_authorized(client: AsyncClient):
    """
    Trying to delete user with auth
    """
    response = await client.post("/users", json=user_data)
    assert response.status_code == 201
    assert exact_schema(user) == response.json()
    assert response.json().get("username") == user_data["username"]

    response = await client.post("/auth/login", json=user_data)
    assert response.status_code == 200
    assert exact_schema(success) == response.json()
    assert list(response.cookies.keys()) == correct_cookies

    cookies = response.cookies
    headers = {"X-CSRF-Token": cookies.get("csrf_access_token")}

    response = await client.delete(f"/users/{user_data['username']}", headers=headers)
    assert response.status_code == 204
    assert len(response.cookies) == 0


@pytest.mark.asyncio
async def test_delete_user_unauthorized(client: AsyncClient):
    """
    Trying to delete user unauthorized
    """
    response = await client.post("/users", json=user_data)
    assert response.status_code == 201
    assert exact_schema(user) == response.json()
    assert response.json().get("username") == user_data["username"]

    response = await client.delete(f"/users/{user_data['username']}")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_another_user(client: AsyncClient):
    """
    Trying to delete another user and not existed_user
    """
    response = await client.post(
        "/users", json={"username": "another_user", "password": "12345678"}
    )
    assert response.status_code == 201
    assert exact_schema(user) == response.json()

    response = await client.post("/users", json=user_data)
    assert response.status_code == 201
    assert exact_schema(user) == response.json()
    assert response.json().get("username") == user_data["username"]

    response = await client.post("/auth/login", json=user_data)
    assert response.status_code == 200
    assert exact_schema(success) == response.json()
    assert list(response.cookies.keys()) == correct_cookies

    cookies = response.cookies
    headers = {"X-CSRF-Token": cookies.get("csrf_access_token")}

    response = await client.delete("/users/another_user", headers=headers)
    assert response.status_code == 405

    response = await client.delete("/users/not_existed_user", headers=headers)
    assert response.status_code == 400
