import pytest
from pytest_schema import exact_schema
from .schemas import success, error
from ..users.schemas import user
from httpx import AsyncClient


correct_cookies: list[str] = [
    "access_token_cookie",
    "csrf_access_token",
    "csrf_refresh_token",
    "refresh_token_cookie",
]

user_data = {"username": "Sam", "password": "sam_password"}


@pytest.mark.asyncio
async def test_auth_not_existed_user(client: AsyncClient):
    """
    Trying to authenticate not existed user
    """
    response = await client.post(
        "/auth/login", json={"username": "not_exists", "password": "12345678"}
    )
    assert response.status_code == 401
    assert response.json().get("detail") == "Bad username or password"


@pytest.mark.asyncio
async def test_auth_existed_user(client: AsyncClient):
    """
    Trying to authenticate existed user
    """
    response = await client.post("/users", json=user_data)
    assert response.status_code == 201
    assert exact_schema(user) == response.json()
    assert response.json().get("username") == user_data["username"]

    response = await client.post("/auth/login", json=user_data)
    assert response.status_code == 200
    assert exact_schema(success) == response.json()
    assert list(response.cookies.keys()) == correct_cookies


@pytest.mark.asyncio
async def test_auth_blank_body(client: AsyncClient):
    """
    Trying to authenticate user with incorrect blank data
    """
    response = await client.post("/auth/login", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_auth_not_valid_data(client: AsyncClient):
    """
    Trying to authenticate user with invalid data
    """
    response = await client.post("/users", json=user_data)
    assert response.status_code == 201
    assert exact_schema(user) == response.json()
    assert response.json().get("username") == user_data["username"]

    response = await client.post(
        "/auth/login", json={"username": "Sam", "password": "123"}
    )
    assert response.status_code == 422

    response = await client.post(
        "/auth/login", json={"username": "Sam", "password": "12345678"}
    )
    assert response.status_code == 401
    assert response.json().get("detail") == "Bad username or password"

    response = await client.post(
        "/auth/login", json={"username": "1234", "password": "123456789"}
    )
    assert response.status_code == 401
    assert response.json().get("detail") == "Bad username or password"

    response = await client.post(
        "/auth/login", json={"username": "1234", "password": "sam_password"}
    )
    assert response.status_code == 401
    assert response.json().get("detail") == "Bad username or password"


@pytest.mark.asyncio
async def test_refresh_access_token(client: AsyncClient):
    """
    Trying to refresh access token
    """
    response = await client.post("/users", json=user_data)
    assert response.status_code == 201
    assert exact_schema(user) == response.json()
    assert response.json().get("username") == user_data["username"]

    response = await client.post("/auth/login", json=user_data)
    assert response.status_code == 200
    assert exact_schema(success) == response.json()
    assert list(response.cookies.keys()) == correct_cookies

    headers = {"X-CSRF-Token": response.cookies.get("csrf_refresh_token")}
    response = await client.post("/auth/refresh", headers=headers)
    assert response.status_code == 200
    assert exact_schema(success) == response.json()

    response = await client.post("/auth/refresh")
    assert response.status_code == 401
    assert exact_schema(error) == response.json()
    assert response.json().get("detail") == "Missing CSRF Token"


@pytest.mark.asyncio
async def test_logout(client: AsyncClient):
    """
    Trying to log out
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

    response = await client.delete("/auth/logout")
    assert response.status_code == 401
    assert exact_schema(error) == response.json()
    assert response.json().get("detail") == "Missing CSRF Token"

    headers = {"X-CSRF-Token": cookies.get("csrf_access_token")}
    response = await client.delete("/auth/logout", headers=headers)
    assert response.status_code == 200
    assert exact_schema(success) == response.json()
    assert len(response.cookies) == 0


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient):
    """
    Trying to get current user
    """
    response = await client.get("/users/me")
    assert response.status_code == 401
    assert exact_schema(error)

    response = await client.post("/users", json=user_data)
    assert response.status_code == 201
    assert exact_schema(user) == response.json()
    assert response.json().get("username") == user_data["username"]

    response = await client.post("/auth/login", json=user_data)
    assert response.status_code == 200
    assert exact_schema(success) == response.json()
    assert list(response.cookies.keys()) == correct_cookies

    response = await client.get("/users/me")
    assert response.status_code == 200
    assert exact_schema(user)
